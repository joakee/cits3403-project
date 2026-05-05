from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import User, Listing, Review, ListingView
from app.forms import StoreSetupForm

bp = Blueprint('store', __name__, url_prefix='/store')


@bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup():
    form = StoreSetupForm(obj=current_user)
    if form.validate_on_submit():
        current_user.is_store = True
        current_user.store_name = form.store_name.data.strip() or None
        current_user.store_address = form.store_address.data.strip() or None
        current_user.contact_phone = form.contact_phone.data.strip() or None
        current_user.contact_email = form.contact_email.data.strip() or None
        db.session.commit()
        flash('Store profile saved.', 'success')
        return redirect(url_for('store.storefront', user_id=current_user.id))
    return render_template('store/setup.html', form=form)


@bp.route('/<int:user_id>')
def storefront(user_id):
    store_user = User.query.get_or_404(user_id)
    if not store_user.is_store:
        abort(404)

    listings = (Listing.query
                .filter_by(seller_id=user_id, is_active=True)
                .order_by(Listing.created_at.desc())
                .all())

    reviews = (Review.query
               .filter_by(reviewed_user_id=user_id)
               .order_by(Review.created_at.desc())
               .all())

    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

    total_listings = Listing.query.filter_by(seller_id=user_id).count()
    sold_count = Listing.query.filter_by(seller_id=user_id, is_active=False).count()

    return render_template('store/storefront.html',
                           store_user=store_user,
                           listings=listings,
                           reviews=reviews,
                           avg_rating=avg_rating,
                           total_listings=total_listings,
                           sold_count=sold_count)


@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_store:
        flash('Set up your store profile first.', 'warning')
        return redirect(url_for('store.setup'))

    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    all_listing_ids = [l.id for l in current_user.listings.all()]

    # View counts
    total_views = 0
    views_30d = 0
    views_7d = 0
    views_today = 0
    if all_listing_ids:
        total_views = db.session.query(func.count(ListingView.id)).filter(
            ListingView.listing_id.in_(all_listing_ids)
        ).scalar() or 0

        views_30d = db.session.query(func.count(ListingView.id)).filter(
            ListingView.listing_id.in_(all_listing_ids),
            ListingView.viewed_at >= thirty_days_ago
        ).scalar() or 0

        views_7d = db.session.query(func.count(ListingView.id)).filter(
            ListingView.listing_id.in_(all_listing_ids),
            ListingView.viewed_at >= seven_days_ago
        ).scalar() or 0

        views_today = db.session.query(func.count(ListingView.id)).filter(
            ListingView.listing_id.in_(all_listing_ids),
            ListingView.viewed_at >= today_start
        ).scalar() or 0

    active_listings = current_user.listings.filter_by(is_active=True).order_by(Listing.created_at.desc()).all()
    sold_listings = current_user.listings.filter_by(is_active=False).all()

    revenue = sum(l.price for l in sold_listings)

    total_saves = sum(l.save_count for l in active_listings + sold_listings)

    # Per-listing view counts for top listings table
    listing_view_counts = {}
    if all_listing_ids:
        rows = db.session.query(ListingView.listing_id, func.count(ListingView.id)).filter(
            ListingView.listing_id.in_(all_listing_ids)
        ).group_by(ListingView.listing_id).all()
        listing_view_counts = {lid: cnt for lid, cnt in rows}

    # Category breakdown (active only)
    category_counts = {}
    for l in active_listings:
        category_counts[l.category] = category_counts.get(l.category, 0) + 1

    # Stock warnings: listings where stock_quantity is not None and <= 5
    stock_warnings = [l for l in active_listings
                      if l.stock_quantity is not None and l.stock_quantity <= 5]

    return render_template('store/dashboard.html',
                           total_views=total_views,
                           views_30d=views_30d,
                           views_7d=views_7d,
                           views_today=views_today,
                           active_listings=active_listings,
                           sold_count=len(sold_listings),
                           revenue=revenue,
                           total_saves=total_saves,
                           listing_view_counts=listing_view_counts,
                           category_counts=category_counts,
                           stock_warnings=stock_warnings)


@bp.route('/admin/verify/<int:user_id>', methods=['POST'])
@login_required
def admin_verify(user_id):
    if not current_user.is_admin:
        abort(403)
    target = User.query.get_or_404(user_id)
    target.is_verified = not target.is_verified
    db.session.commit()
    state = 'verified' if target.is_verified else 'unverified'
    flash(f'{target.username} has been {state}.', 'success')
    return redirect(request.referrer or url_for('store.storefront', user_id=user_id))
