from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User, Listing
from app.forms import EditProfileForm, ChangeEmailForm, ChangePasswordForm, DeleteAccountForm

bp = Blueprint('profile', __name__, url_prefix='/user')


@bp.route('/<int:user_id>')
def view(user_id):
    profile_user = User.query.get_or_404(user_id)
    listing_filter = request.args.get('filter', 'active')  # active | sold | all

    base_q = Listing.query.filter_by(seller_id=user_id)
    if listing_filter == 'sold':
        displayed = base_q.filter_by(is_active=False).order_by(Listing.created_at.desc()).all()
    elif listing_filter == 'all':
        displayed = base_q.order_by(Listing.created_at.desc()).all()
    else:  # default: active
        listing_filter = 'active'
        displayed = base_q.filter_by(is_active=True).order_by(Listing.created_at.desc()).all()

    total_listings = base_q.count()
    active_count  = base_q.filter_by(is_active=True).count()
    sold_count    = base_q.filter_by(is_active=False).count()

    return render_template(
        'profile/view.html',
        profile_user=profile_user,
        displayed_listings=displayed,
        listing_filter=listing_filter,
        active_count=active_count,
        total_listings=total_listings,
        sold_count=sold_count,
    )


@bp.route('/me')
@login_required
def me():
    return redirect(url_for('profile.view', user_id=current_user.id))


@bp.route('/me/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('profile.view', user_id=current_user.id))
    return render_template('profile/edit.html', form=form)


@bp.route('/me/settings', methods=['GET'])
@login_required
def settings():
    email_form = ChangeEmailForm(prefix='email')
    password_form = ChangePasswordForm(prefix='password')
    delete_form = DeleteAccountForm(prefix='delete')
    return render_template(
        'profile/settings.html',
        email_form=email_form,
        password_form=password_form,
        delete_form=delete_form,
    )


@bp.route('/me/settings/email', methods=['POST'])
@login_required
def settings_email():
    email_form = ChangeEmailForm(prefix='email')
    if email_form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, email_form.current_password.data):
            flash('Incorrect password.', 'error')
        else:
            current_user.email = email_form.email.data
            db.session.commit()
            flash('Email address updated.', 'success')
    else:
        for field_errors in email_form.errors.values():
            for error in field_errors:
                flash(error, 'error')
    return redirect(url_for('profile.settings'))


@bp.route('/me/settings/password', methods=['POST'])
@login_required
def settings_password():
    password_form = ChangePasswordForm(prefix='password')
    if password_form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, password_form.current_password.data):
            flash('Incorrect current password.', 'error')
        else:
            current_user.password_hash = generate_password_hash(
                password_form.new_password.data, method='pbkdf2:sha256'
            )
            db.session.commit()
            flash('Password updated successfully.', 'success')
    else:
        for field_errors in password_form.errors.values():
            for error in field_errors:
                flash(error, 'error')
    return redirect(url_for('profile.settings'))


@bp.route('/me/settings/delete', methods=['POST'])
@login_required
def settings_delete():
    delete_form = DeleteAccountForm(prefix='delete')
    if delete_form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, delete_form.password.data):
            flash('Incorrect password.', 'error')
            return redirect(url_for('profile.settings'))
        user = current_user._get_current_object()
        logout_user()
        Listing.query.filter_by(seller_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        flash('Your account has been deleted.', 'info')
        return redirect(url_for('auth.register'))
    for field_errors in delete_form.errors.values():
        for error in field_errors:
            flash(error, 'error')
    return redirect(url_for('profile.settings'))
