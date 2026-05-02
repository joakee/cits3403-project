import os
import uuid
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify, current_app)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Listing, ListingEdit
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
    query = Listing.query.filter_by(is_active=True)
    if q:
        query = query.filter(Listing.title.ilike(f'%{q}%'))
    if cat:
        query = query.filter(Listing.category == cat)
    listings = query.order_by(Listing.created_at.desc()).all()
    return render_template('listings/index.html', listings=listings, q=q, cat=cat)


@bp.route('/api/search')
def api_search():
    q = request.args.get('q', '').strip()
    query = Listing.query.filter_by(is_active=True)
    if q:
        query = query.filter(Listing.title.ilike(f'%{q}%'))
    results = query.order_by(Listing.created_at.desc()).limit(20).all()
    return jsonify([{
        'id': l.id,
        'title': l.title,
        'price': l.price,
        'category': l.category,
        'image_url': l.image_url,
    } for l in results])


@bp.route('/<int:listing_id>')
def detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
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
