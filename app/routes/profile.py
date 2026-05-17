import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, abort
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User, Listing, Review, Wishlist
from app.forms import EditProfileForm, ReviewForm, ChangeEmailForm, ChangePasswordForm, DeleteAccountForm

bp = Blueprint('profile', __name__, url_prefix='/user')

@bp.before_request
def enforce_verification():
    if current_user.is_authenticated:
        # Routes an unverified user is ALLOWED to see
        allowed_routes = ['auth.verify_email', 'auth.resend_otp', 'auth.logout', 'static']
        
        if not current_user.is_verified and request.endpoint not in allowed_routes:
            return redirect(url_for('auth.verify_email'))

PROFILE_PER_PAGE = 12


@bp.route('/<int:user_id>')
def view(user_id):
    profile_user = User.query.get_or_404(user_id)
    listing_filter = request.args.get('filter', 'active')
    page = request.args.get('page', 1, type=int)

    # Show personal user listings on the profile page.
    # Store listings are handled separately by the store page.
    base_q = Listing.query.filter_by(seller_id=user_id, posted_as_store=False)

    if listing_filter == 'sold':
        paged = base_q.filter_by(is_active=False).order_by(Listing.created_at.desc())
    elif listing_filter == 'all':
        paged = base_q.order_by(Listing.created_at.desc())
    else:
        listing_filter = 'active'
        paged = base_q.filter_by(is_active=True).order_by(Listing.created_at.desc())

    pagination = paged.paginate(page=page, per_page=PROFILE_PER_PAGE, error_out=False)

    all_seller_listings = base_q.all()

    total_listings = len(all_seller_listings)
    active_count = sum(1 for listing in all_seller_listings if listing.is_active)
    sold_count = sum(1 for listing in all_seller_listings if not listing.is_active)

    # Seller data / analytics
    total_views = sum((listing.view_count or 0) for listing in all_seller_listings)
    total_saves = sum(listing.save_count for listing in all_seller_listings)

    reviews = Review.query.filter_by(reviewed_user_id=user_id).order_by(Review.created_at.desc()).all()

    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

    return render_template(
        'profile/view.html',
        profile_user=profile_user,
        displayed_listings=pagination.items,
        pagination=pagination,
        listing_filter=listing_filter,
        active_count=active_count,
        total_listings=total_listings,
        sold_count=sold_count,
        total_views=total_views,
        total_saves=total_saves,
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

        if form.avatar.data and form.avatar.data.filename:
            current_user.avatar_url = _save_avatar(form.avatar.data)

        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('profile.view', user_id=current_user.id))

    return render_template('profile/edit.html', form=form)


def _save_avatar(file_storage):
    allowed = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

    ext = file_storage.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed:
        return current_user.avatar_url

    filename = f"avatar_{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file_storage.save(os.path.join(upload_folder, filename))

    return url_for('static', filename=f'uploads/{filename}')


@bp.route('/me/settings')
@login_required
def settings():
    return render_template(
        'profile/settings.html',
        email_form=ChangeEmailForm(),
        password_form=ChangePasswordForm(),
        delete_form=DeleteAccountForm()
    )


@bp.route('/me/settings/email', methods=['POST'])
@login_required
def settings_email():
    form = ChangeEmailForm()

    if form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Incorrect password.', 'error')
        else:
            current_user.email = form.email.data
            db.session.commit()
            flash('Email updated.', 'success')
    else:
        for field_errors in form.errors.values():
            for e in field_errors:
                flash(e, 'error')

    return redirect(url_for('profile.settings'))


@bp.route('/me/settings/password', methods=['POST'])
@login_required
def settings_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Incorrect current password.', 'error')
        else:
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Password updated.', 'success')
    else:
        for field_errors in form.errors.values():
            for e in field_errors:
                flash(e, 'error')

    return redirect(url_for('profile.settings'))


@bp.route('/me/settings/delete', methods=['POST'])
@login_required
def settings_delete():
    form = DeleteAccountForm()

    if form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, form.password.data):
            flash('Incorrect password.', 'error')
            return redirect(url_for('profile.settings'))

        from flask_login import logout_user
        from app.models import Conversation, Message, ListingView
        from sqlalchemy import or_

        user = current_user._get_current_object()

        # Remove all user wishlists
        for wl in user.wishlists.all():
            db.session.delete(wl)

        # Remove all user listings and related listing views
        for listing in user.listings.all():
            ListingView.query.filter_by(listing_id=listing.id).delete()
            db.session.delete(listing)

        # Remove conversations involving this user
        convs = Conversation.query.filter(
            or_(Conversation.buyer_id == user.id, Conversation.seller_id == user.id)
        ).all()

        for conv in convs:
            Message.query.filter_by(conversation_id=conv.id).delete()
            db.session.delete(conv)

        # Remove reviews written by or about this user
        Review.query.filter(
            (Review.reviewer_id == user.id) | (Review.reviewed_user_id == user.id)
        ).delete()

        db.session.delete(user)
        db.session.commit()

        logout_user()
        flash('Your account has been deleted.', 'info')
        return redirect(url_for('index'))

    flash('Could not delete account.', 'error')
    return redirect(url_for('profile.settings'))


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
    """AJAX: move a listing from wl_id into target_id."""
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


@bp.route('/<int:user_id>/toggle-ban', methods=['POST'])
@login_required
def toggle_user_ban(user_id):
    # Only true administrators can ban/unban users
    if not current_user.is_admin:
        abort(403)

    if current_user.id == user_id:
        flash("You cannot ban your own account!", "danger")
        return redirect(url_for('profile.view', user_id=user_id))

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active

    for listing in user.listings:
        listing.is_active = False

    db.session.commit()

    action_taken = "banned" if not user.is_active else "unbanned"
    flash(f"User {user.username} has been {action_taken}.", "warning")

    return redirect(url_for('profile.view', user_id=user.id))