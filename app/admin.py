from flask import redirect, url_for, request, flash
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask_login import current_user
from flask_admin.theme import Bootstrap4Theme
from sqlalchemy import func

from app import db 
from app.models import User, Listing, Conversation, Message

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        flash("You do not have permission to view this page.", "danger")
        return redirect(url_for('auth.login', next=request.url))

class SecureAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))
    
    @expose('/')
    def index(self):
        # 1. High-level counts
        user_count = User.query.count()
        listing_count = Listing.query.count()
        total_messages = Message.query.count()
        
        # 2. Financial Analytics (Sum of active listing prices)
        total_market_value = db.session.query(func.sum(Listing.price)).filter_by(is_active=True).scalar() or 0
        
        # 3. Category Distribution
        category_data = db.session.query(
            Listing.category, func.count(Listing.id)
        ).group_by(Listing.category).all()

        # 4. Recent Activity (Last 5 listings)
        recent_listings = Listing.query.order_by(Listing.created_at.desc()).limit(5).all()

        return self.render('admin/index.html', 
                           user_count=user_count,
                           listing_count=listing_count,
                           total_messages=total_messages,
                           total_market_value=total_market_value,
                           category_data=category_data,
                           recent_listings=recent_listings)

class ListingAdminView(SecureModelView):
    column_list = ('title', 'seller', 'price', 'is_active', 'created_at')
    column_searchable_list = ['title', 'description']
    column_filters = ['is_active', 'category']

    @action('toggle_active', 'Toggle Active Status', 'Are you sure you want to toggle the active status of selected listings?')
    def action_toggle_active(self, ids):
        try:
            query = Listing.query.filter(Listing.id.in_(ids))
            count = 0
            for listing in query.all():
                listing.is_active = not listing.is_active
                count += 1
            db.session.commit()
            flash(f'{count} listings were successfully updated.', 'success')
        except Exception as ex:
            db.session.rollback()
            flash(f'Failed to update listings. {str(ex)}', 'error')

def init_admin(app):
    """Initializes the admin panel and binds it to the Flask app."""
    admin = Admin(
        app, 
        name='Marketplace Admin', 
        theme=Bootstrap4Theme(swatch='slate'),
        index_view=SecureAdminIndexView()
    )
    
    # Add views to the admin panel
    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(ListingAdminView(Listing, db.session))
    admin.add_view(SecureModelView(Conversation, db.session))
    admin.add_view(SecureModelView(Message, db.session))