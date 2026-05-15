from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, mail
import app
from app.models import User
from app.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from datetime import datetime, timedelta
from flask_mail import Message

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_request
def check_verification():
    if current_user.is_authenticated:
        # Allow them to access the verify page, static files, and logout
        allowed_routes = ['auth.verify_email', 'auth.logout', 'static']
        if not current_user.is_verified and request.endpoint not in allowed_routes:
            flash("Please verify your email to continue.", "info")
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
        db.session.add(user)
        db.session.commit()
        
        msg = Message('Your Marketplace OTP', sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[user.email])
        msg.body = f'Your verification code is: {otp}'
        try:
            mail.send(msg)
        except Exception as e:
            # It's good practice to log this or flash a message if the email server fails
            print(f"Mail error: {e}")
            flash("We couldn't send a verification email. Please try again later.", "danger")
        
        # Log them in but keep is_verified=False
        login_user(user) 
        return redirect(url_for('auth.verify_email'))
        # db.session.add(user)
        # db.session.commit()
        # login_user(user)
        # flash('Account created! Welcome to UWA Marketplace.', 'success')
        # return redirect(url_for('listings.index'))
    return render_template('auth/register.html', form=form)

@bp.route('/verify-email', methods=['GET', 'POST'])
@login_required
def verify_email():
    if current_user.is_verified:
        return redirect(url_for('index'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp')
    
        # 1. Check attempts
        if current_user.otp_attempts >= 5:
            flash("Too many failed attempts. Please request a new code.", "danger")
            return redirect(url_for('auth.verify_email'))

        # 2. Check validity
        if current_user.otp_code == entered_otp and datetime.utcnow() < current_user.otp_expiry:
            current_user.is_verified = True
            current_user.otp_attempts = 0 # Reset
            db.session.commit()
            return redirect(url_for('index'))
        else:
            current_user.otp_attempts += 1 # Increment
            db.session.commit()
            flash(f"Invalid code. {5 - current_user.otp_attempts} attempts remaining.", "danger")
            
    return render_template('auth/verify_email.html')

@bp.route('/resend-otp')
@login_required
def resend_otp():
    if current_user.is_verified:
        return redirect(url_for('index'))

    # Check for cool-down (e.g., must wait 60 seconds since last expiry set)
    # We subtract 9 minutes from expiry to see when it was last generated
    # (Since we set expiry to +10 mins)
    last_generated = current_user.otp_expiry - timedelta(minutes=10)
    now = datetime.utcnow()

    if now < last_generated + timedelta(seconds=60):
        time_left = 60 - (now - last_generated).seconds
        flash(f"Please wait {time_left} seconds before requesting a new code.", "warning")
        return redirect(url_for('auth.verify_email'))

    # Generate and send new code
    otp = current_user.generate_otp()
    db.session.commit()

    msg = Message('Your New Marketplace OTP', 
                  sender=current_app.config['MAIL_DEFAULT_SENDER'], 
                  recipients=[current_user.email])
    msg.body = f'Your new verification code is: {otp}'
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