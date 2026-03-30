from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Listing
from app.forms import EditProfileForm

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
