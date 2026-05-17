from flask import Blueprint, render_template
from app.models import Listing, User

bp = Blueprint('legal', __name__, url_prefix='/legal')


@bp.route('/about')
def about():
    total_listings = Listing.query.filter_by(is_active=True, is_removed=False).count()
    total_users = User.query.count()
    return render_template('legal/about.html',
                           total_listings=total_listings,
                           total_users=total_users)


@bp.route('/faq')
def faq():
    return render_template('legal/faq.html')


@bp.route('/terms')
def tos():
    return render_template('legal/tos.html')


@bp.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')
