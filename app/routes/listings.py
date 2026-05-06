import os
import uuid
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify, current_app, abort)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Listing, ListingEdit, User, Wishlist
from app.forms import ListingForm, EditListingForm

bp = Blueprint('listings', __name__, url_prefix='/listings')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def _save_image(file_storage):
    """Save an uploaded image and return its URL path, or None."""
    if not file_storage or file_storage.filename == '':
        return None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file_storage.save(os.path.join(upload_folder, filename))
    return url_for('static', filename=f'uploads/{filename}')


@bp.route('/')
def index():
    q   = request.args.get('q', '').strip()
    cat = request.args.get('category', '').strip()
    query = Listing.query.filter_by(is_active=True, is_removed=False)
    if q:
        query = query.filter(Listing.title.ilike(f'%{q}%'))
    if cat:
        query = query.filter(Listing.category == cat)
    listings = query.order_by(Listing.created_at.desc()).all()
    return render_template('listings/index.html', listings=listings, q=q, cat=cat)


@bp.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip()
    query = Listing.query.filter_by(is_active=True, is_removed=False)
    if q:
        query = query.filter(Listing.title.ilike(f'%{q}%'))
    results = query.order_by(Listing.created_at.desc()).limit(20).all()
    
    wishlisted_ids = set()
    if current_user.is_authenticated:
        wishlisted_ids = {l.id for l in current_user.wishlist_listings}

    return jsonify([{
        'id': l.id,
        'title': l.title,
        'price': l.price,
        'category': l.category,
        'image_url': l.image_url,
        'seller_id': l.seller.id,
        'seller_username': l.seller.username,
        'is_wishlisted': l.id in wishlisted_ids,
        'wishlist_count': l.wishlisted_by.count()
    } for l in results])


@bp.route('/<int:listing_id>')
def detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.is_removed:
        if current_user.is_authenticated and (current_user.is_admin or current_user.is_moderator):
            pass
        else:
            flash('This listing has been removed by moderation.', 'warning')
            return redirect(url_for('listings.index'))
    return render_template('listings/detail.html', listing=listing)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = ListingForm()
    if form.validate_on_submit():
        image_url = _save_image(form.image.data)
        listing = Listing(
            title=form.title.data,
            description=form.description.data,
            price=float(form.price.data),
            category=form.category.data,
            image_url=image_url,
            seller_id=current_user.id,
        )
        db.session.add(listing)
        db.session.commit()
        flash('Listing posted!', 'success')
        return redirect(url_for('listings.detail', listing_id=listing.id))
    return render_template('listings/new.html', form=form)


@bp.route('/<int:listing_id>/close', methods=['POST'])
@login_required
def close(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.seller_id != current_user.id:
        flash('Not authorised.', 'error')
        return redirect(url_for('listings.detail', listing_id=listing_id))
    if listing.is_removed and not (current_user.is_admin or current_user.is_moderator):
        abort(404)
    listing.is_active = False
    db.session.commit()
    flash('Listing marked as sold.', 'success')
    return redirect(url_for('profile.view', user_id=current_user.id))


@bp.route('/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.seller_id != current_user.id:
        flash('Not authorised.', 'error')
        return redirect(url_for('listings.detail', listing_id=listing_id))
    if listing.is_removed and not (current_user.is_admin or current_user.is_moderator):
        abort(404)

    form = EditListingForm(obj=listing)
    if form.validate_on_submit():
        changes_made = False

        # Check standard text/number fields
        fields_to_check = ['title', 'description', 'price', 'category']
        for field in fields_to_check:
            old_val = getattr(listing, field)
            new_val = getattr(form, field).data
            
            # Form price is Decimal, model is float. Convert new_val to float for comparison.
            if field == 'price':
                new_val = float(new_val)

            if old_val != new_val:
                edit_log = ListingEdit(
                    listing_id=listing.id,
                    field_name=field,
                    old_value=str(old_val),
                    new_value=str(new_val)
                )
                db.session.add(edit_log)
                setattr(listing, field, new_val)
                changes_made = True

        # Handle image separately (don't log image changes in history text)
        if form.image.data:
            image_url = _save_image(form.image.data)
            if image_url:
                listing.image_url = image_url
                changes_made = True

        # Handle history visibility toggle (don't log this as an edit)
        if listing.show_history != form.show_history.data:
            listing.show_history = form.show_history.data
            changes_made = True

        if changes_made:
            db.session.commit()
            flash('Listing updated successfully.', 'success')
        else:
            flash('No changes were made.', 'info')
            
        return redirect(url_for('listings.detail', listing_id=listing.id))

    # Pre-populate boolean on GET
    if request.method == 'GET':
        form.show_history.data = listing.show_history

    return render_template('listings/edit.html', form=form, listing=listing)

@bp.route('/<int:listing_id>/toggle-active', methods=['POST'])
@login_required
def toggle_listing_active(listing_id):
    # Check if the user has moderation or admin rights
    if not (current_user.is_admin or current_user.is_moderator):
        abort(403) # Forbidden

    listing = Listing.query.get_or_404(listing_id)
    listing.is_active = not listing.is_active
    db.session.commit()

    status = "restored" if listing.is_active else "taken down"
    flash(f"Listing '{listing.title}' has been successfully {status}.", "success")
    
    return redirect(url_for('listings.detail', listing_id=listing.id))

@bp.route('/<int:listing_id>/wishlist', methods=['POST'])
@login_required
def toggle_wishlist(listing_id):
    """Legacy toggle - saves to first/default wishlist. Kept for non-JS fallback."""
    listing = Listing.query.get_or_404(listing_id)
    if listing.is_removed and not (current_user.is_admin or current_user.is_moderator):
        abort(404)
    added = False

    # Get or create default wishlist
    default_wl = current_user.wishlists.order_by(Wishlist.created_at.asc()).first()
    if not default_wl:
        default_wl = Wishlist(name="Saved Items", user_id=current_user.id)
        db.session.add(default_wl)
        db.session.commit()

    if listing in default_wl.listings:
        default_wl.listings.remove(listing)
        flash('Removed from wishlist.', 'info')
    else:
        default_wl.listings.append(listing)
        added = True
        flash('Added to wishlist.', 'success')
    db.session.commit()

    wishlist_count = listing.save_count

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': True, 'added': added, 'count': wishlist_count})

    next_page = request.referrer or url_for('listings.detail', listing_id=listing.id)
    return redirect(next_page)


@bp.route('/<int:listing_id>/wishlists', methods=['GET'])
@login_required
def get_wishlists_for_listing(listing_id):
    """Return user's wishlists with checked status for this listing."""
    listing = Listing.query.get_or_404(listing_id)
    if listing.is_removed and not (current_user.is_admin or current_user.is_moderator):
        return jsonify({'error': 'Listing not found'}), 404
    wishlists = current_user.wishlists.order_by(Wishlist.created_at.asc()).all()

    # Auto-create default if none
    if not wishlists:
        default_wl = Wishlist(name="Saved Items", user_id=current_user.id)
        db.session.add(default_wl)
        db.session.commit()
        wishlists = [default_wl]

    return jsonify({
        'wishlists': [{
            'id': wl.id,
            'name': wl.name,
            'checked': listing in wl.listings
        } for wl in wishlists],
        'save_count': listing.save_count,
        'is_saved': current_user.has_saved(listing)
    })


@bp.route('/<int:listing_id>/wishlist/<int:wishlist_id>', methods=['POST'])
@login_required
def toggle_wishlist_item(listing_id, wishlist_id):
    """Toggle a listing in a specific wishlist."""
    listing = Listing.query.get_or_404(listing_id)
    if listing.is_removed and not (current_user.is_admin or current_user.is_moderator):
        return jsonify({'error': 'Listing not found'}), 404
    wl = Wishlist.query.filter_by(id=wishlist_id, user_id=current_user.id).first_or_404()

    if listing in wl.listings:
        wl.listings.remove(listing)
        checked = False
    else:
        wl.listings.append(listing)
        checked = True
    db.session.commit()

    return jsonify({
        'success': True,
        'checked': checked,
        'save_count': listing.save_count,
        'is_saved': current_user.has_saved(listing)
    })
