from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Listing, Review
from app.forms import EditProfileForm, ReviewForm

bp = Blueprint('profile', __name__, url_prefix='/user')


@bp.route('/<int:user_id>')
def view(user_id):
    profile_user = User.query.get_or_404(user_id)
    listing_filter = request.args.get('filter', 'active')

    base_q = Listing.query.filter_by(seller_id=user_id)
    if listing_filter == 'sold':
        displayed = base_q.filter_by(is_active=False).order_by(Listing.created_at.desc()).all()
    elif listing_filter == 'all':
        displayed = base_q.order_by(Listing.created_at.desc()).all()
    else:
        listing_filter = 'active'
        displayed = base_q.filter_by(is_active=True).order_by(Listing.created_at.desc()).all()

    total_listings = base_q.count()
    active_count = base_q.filter_by(is_active=True).count()
    sold_count = base_q.filter_by(is_active=False).count()

    reviews = Review.query.filter_by(reviewed_user_id=user_id).order_by(Review.created_at.desc()).all()

    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

    return render_template(
        'profile/view.html',
        profile_user=profile_user,
        displayed_listings=displayed,
        listing_filter=listing_filter,
        active_count=active_count,
        total_listings=total_listings,
        sold_count=sold_count,
        reviews=reviews,
        avg_rating=avg_rating,
    )


@bp.route('/<int:user_id>/review', methods=['GET', 'POST'])
@login_required
def review_user(user_id):
    profile_user = User.query.get_or_404(user_id)

    if profile_user.id == current_user.id:
        flash('You cannot review yourself.', 'error')
        return redirect(url_for('profile.view', user_id=profile_user.id))

    form = ReviewForm()

    if form.validate_on_submit():
        review = Review(
            rating=int(form.rating.data),
            comment=form.comment.data,
            reviewer_id=current_user.id,
            reviewed_user_id=profile_user.id
        )
        db.session.add(review)
        db.session.commit()
        flash('Review submitted successfully.', 'success')
        return redirect(url_for('profile.view', user_id=profile_user.id))

    return render_template('profile/review.html', form=form, profile_user=profile_user)


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


@bp.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = current_user.wishlist_listings.filter(Listing.is_active == True).order_by(Listing.created_at.desc()).all()
    return render_template('profile/wishlist.html', listings=wishlist_items)