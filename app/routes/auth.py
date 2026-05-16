from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User
from app.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('listings.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.is_active:
                flash("Your account has been suspended. Please contact support.", "danger")
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
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
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created! Welcome to UWA Marketplace.', 'success')
        return redirect(url_for('listings.index'))
    return render_template('auth/register.html', form=form)


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