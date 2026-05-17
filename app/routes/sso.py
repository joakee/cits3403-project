import secrets
from flask import Blueprint, redirect, url_for, flash, current_app, session, request
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash
from authlib.integrations.base_client.errors import OAuthError
from app import db, csrf
from app.models import User
from app.oauth import oauth

bp = Blueprint('sso', __name__, url_prefix='/auth/microsoft')


def _email_domain_allowed(email: str) -> bool:
    if not email or '@' not in email:
        return False
    domain = email.rsplit('@', 1)[1].lower().strip()
    allowed = [d.strip().lower() for d in current_app.config.get('SSO_ALLOWED_EMAIL_DOMAINS', [])]
    return domain in allowed


def _unique_username(base: str) -> str:
    base = (base or 'user').strip().replace(' ', '').lower() or 'user'
    candidate = base
    i = 1
    while User.query.filter_by(username=candidate).first() is not None:
        i += 1
        candidate = f"{base}{i}"
    return candidate


@bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('listings.index'))
    redirect_uri = current_app.config.get('MICROSOFT_REDIRECT_URI') \
        or url_for('sso.callback', _external=True)
    return oauth.microsoft.authorize_redirect(redirect_uri)


@bp.route('/callback')
@csrf.exempt  # OAuth uses its own `state` parameter for CSRF protection
def callback():
    try:
        token = oauth.microsoft.authorize_access_token()
    except OAuthError as e:
        current_app.logger.warning(f"Microsoft OAuth error: {e}")
        flash('Microsoft sign-in failed or was cancelled.', 'danger')
        return redirect(url_for('auth.login'))

    userinfo = token.get('userinfo') or oauth.microsoft.parse_id_token(token, nonce=None)
    if not userinfo:
        flash('Could not read Microsoft account info.', 'danger')
        return redirect(url_for('auth.login'))

    sub = userinfo.get('sub')
    email = (userinfo.get('email') or userinfo.get('preferred_username') or '').lower()
    name = userinfo.get('name') or email.split('@')[0]

    if not sub or not email:
        flash('Microsoft account is missing required fields.', 'danger')
        return redirect(url_for('auth.login'))

    if not _email_domain_allowed(email):
        allowed = ', '.join(current_app.config.get('SSO_ALLOWED_EMAIL_DOMAINS', []))
        flash(f'Only UWA Microsoft accounts are allowed ({allowed}).', 'danger')
        return redirect(url_for('auth.login'))

    # 1) Match by microsoft_sub (returning SSO user)
    user = User.query.filter_by(microsoft_sub=sub).first()

    # 2) Else match by email and link the account
    if user is None:
        user = User.query.filter_by(email=email).first()
        if user is not None:
            user.microsoft_sub = sub
            if not user.is_verified:
                user.is_verified = True
            db.session.commit()

    # 3) Else provision a new user
    if user is None:
        user = User(
            username=_unique_username(name),
            email=email,
            password_hash=generate_password_hash(secrets.token_urlsafe(32), method='pbkdf2:sha256'),
            is_verified=True,
            microsoft_sub=sub,
        )
        db.session.add(user)
        db.session.commit()

    if not user.is_active:
        flash('Your account has been suspended. Please contact support.', 'danger')
        return redirect(url_for('auth.login'))

    login_user(user, remember=True)
    flash(f'Signed in as {user.email} via Microsoft.', 'success')
    return redirect(url_for('listings.index'))
