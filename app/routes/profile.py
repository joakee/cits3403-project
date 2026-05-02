from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Listing, Review, Wishlist
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


@bp.route('/wishlist', methods=['GET', 'POST'])
@login_required
def wishlist():
    if request.method == 'POST':
        name = request.form.get('name')
        if name and name.strip():
            new_wl = Wishlist(name=name.strip(), user_id=current_user.id)
            db.session.add(new_wl)
            db.session.commit()
            flash(f'Wishlist "{name}" created.', 'success')
        return redirect(url_for('profile.wishlist'))

    wishlists = current_user.wishlists.order_by(Wishlist.created_at.asc()).all()
    if not wishlists:
        default_wl = Wishlist(name="Saved Items", user_id=current_user.id)
        db.session.add(default_wl)
        db.session.commit()
        wishlists = [default_wl]

    return render_template('profile/wishlist.html', wishlists=wishlists)


@bp.route('/wishlist/create', methods=['POST'])
@login_required
def wishlist_create():
    """AJAX: create a new wishlist, return {id, name}."""
    name = request.json.get('name', '').strip() if request.is_json else request.form.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    wl = Wishlist(name=name, user_id=current_user.id)
    db.session.add(wl)
    db.session.commit()
    return jsonify({'id': wl.id, 'name': wl.name})


@bp.route('/wishlist/<int:wl_id>/rename', methods=['POST'])
@login_required
def wishlist_rename(wl_id):
    """AJAX: rename a wishlist."""
    wl = Wishlist.query.filter_by(id=wl_id, user_id=current_user.id).first_or_404()
    name = request.json.get('name', '').strip() if request.is_json else request.form.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    wl.name = name
    db.session.commit()
    return jsonify({'id': wl.id, 'name': wl.name})


@bp.route('/wishlist/<int:wl_id>/delete', methods=['POST'])
@login_required
def wishlist_delete(wl_id):
    """AJAX: delete a wishlist."""
    wl = Wishlist.query.filter_by(id=wl_id, user_id=current_user.id).first_or_404()
    db.session.delete(wl)
    db.session.commit()
    return jsonify({'success': True})


@bp.route('/wishlist/<int:wl_id>/move/<int:listing_id>', methods=['POST'])
@login_required
def wishlist_move(wl_id, listing_id):
    """AJAX: move a listing from wl_id into target_id (remove from source, add to target)."""
    target_id = request.json.get('target_id') if request.is_json else request.form.get('target_id')
    if not target_id:
        return jsonify({'error': 'target_id required'}), 400
    source_wl = Wishlist.query.filter_by(id=wl_id, user_id=current_user.id).first_or_404()
    target_wl = Wishlist.query.filter_by(id=int(target_id), user_id=current_user.id).first_or_404()
    listing = Listing.query.get_or_404(listing_id)
    if listing in source_wl.listings:
        source_wl.listings.remove(listing)
    if listing not in target_wl.listings:
        target_wl.listings.append(listing)
    db.session.commit()
    return jsonify({'success': True})