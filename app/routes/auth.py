from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, mail
import app
from app.models import User
from app.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from datetime import datetime, timedelta
from flask_mail import Message
import random

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_request
def enforce_verification():
    if current_user.is_authenticated:
        allowed_routes = ['auth.verify_email', 'auth.resend_otp', 'auth.logout', 'static']
        
        if not current_user.is_verified and request.endpoint not in allowed_routes:
            return redirect(url_for('auth.verify_email'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('listings.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if not user.is_active:
                flash("Your account has been suspended. Please contact support.", "danger")
                return redirect(url_for('auth.login'))
            if not user.is_verified:
                flash("Your account has not been verified. Please verify your account.", "danger")
                return redirect(url_for('auth.verify_email'))
            return redirect(next_page or url_for('listings.index'))
        flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('listings.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data, method='pbkdf2:sha256'),
        )
        otp = user.generate_otp()

        session['pending_user'] = {
            'username': user.username,
            'email': user.email,
            'password_hash': user.password_hash,
            'otp_code': generate_password_hash(otp, method='pbkdf2:sha256'),
            'otp_expiry': (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
            'otp_attempts': 0
        }

        msg = Message('Your Marketplace OTP', sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[user.email])
        msg.body = f'Your verification code is: {otp}'
        
        try:
            mail.send(msg)
            flash("Verification email sent. Make sure to check your spam folder!", "success")
        except Exception as e:
            print(f"Mail error: {e}")
            flash("We couldn't send a verification email. Please try again later.", "danger")
        
        return redirect(url_for('auth.verify_email'))
    return render_template('auth/register.html', form=form)

@bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    pending = session.get('pending_user')
    if not pending:
        flash("No registration in progress. Please sign up.", "warning")
        return redirect(url_for('auth.register'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        expiry_time = datetime.fromisoformat(pending['otp_expiry'])
        
        if pending['otp_attempts'] >= 5:
            session.pop('pending_user', None) 
            flash("Too many failed attempts. Please register again.", "danger")
            return redirect(url_for('auth.register'))

        if check_password_hash(pending['otp_code'], entered_otp) and datetime.utcnow() < expiry_time:
            new_user = User(
                username=pending['username'],
                email=pending['email'],
                password_hash=pending['password_hash'],
                is_verified=True 
            )
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            session.pop('pending_user', None)

            flash("Account successfully created! You can now log in.", "success")
            return redirect(url_for('listings.index'))
        else:
            pending['otp_attempts'] += 1
            session.modified = True 
            flash("Invalid or expired verification code.", "danger")
            
    return render_template('auth/verify_email.html')

@bp.route('/resend-otp')
def resend_otp():
    pending = session.get('pending_user')
    if not pending:
        flash("No registration in progress. Please sign up.", "warning")
        return redirect(url_for('auth.register')) 

    last_generated = datetime.fromisoformat(pending['otp_expiry']) - timedelta(minutes=10)
    now = datetime.utcnow()

    if pending['otp_attempts'] >= 5:
        session.pop('pending_user', None) # Force wipe their stale session data
        flash("Too many failed verification attempts. Please start your registration over.", "danger")
        return redirect(url_for('auth.register'))

    if now < last_generated + timedelta(seconds=60):
        time_left = 60 - (now - last_generated).seconds
        flash(f"Please wait {time_left} seconds before requesting a new code.", "warning")
        return redirect(url_for('auth.verify_email'))

    new_otp = f"{random.randint(100000, 999999)}"
    new_expiry = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    
    # 4. Update the session dictionary values (Hashing the OTP for client-side security)
    pending['otp_code'] = generate_password_hash(new_otp, method='pbkdf2:sha256')
    pending['otp_expiry'] = new_expiry

    msg = Message('Your New Marketplace OTP', 
                  sender=current_app.config['MAIL_DEFAULT_SENDER'], 
                  recipients=[pending['email']])
    msg.body = f'Your new verification code is: {new_otp}'
    mail.send(msg)

    flash("A new code has been sent to your email.", "success")
    return redirect(url_for('auth.verify_email'))

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('listings.index'))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            session['reset_email'] = user.email
            return redirect(url_for('auth.reset_password'))

        flash('No account found with that email.', 'error')

    return render_template('auth/forgot_password.html', form=form)


@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('listings.index'))

    email = session.get('reset_email')

    if not email:
        flash('Please start from the forgot password page.', 'error')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()

    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        db.session.commit()
        session.pop('reset_email', None)
        flash('Password reset successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))