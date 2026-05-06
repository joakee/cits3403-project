from datetime import timedelta
from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from config import Config
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins='*')
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.routes.auth import bp as auth_bp
    from app.routes.profile import bp as profile_bp
    from app.routes.listings import bp as listings_bp
    from app.routes.chat import bp as chat_bp
    from app.routes.moderation import bp as moderation_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(moderation_bp)

    from app.admin import init_admin
    init_admin(app)

    socketio.init_app(app)

    @socketio.on('connect')
    def handle_connect():
        print('[socketio] Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('[socketio] Client disconnected')

    @app.context_processor
    def inject_wishlist_count():
        if current_user.is_authenticated:
            from app.models import Wishlist, wishlist_items
            from sqlalchemy import func
            count = db.session.query(func.count(wishlist_items.c.listing_id)).join(
                Wishlist, Wishlist.id == wishlist_items.c.wishlist_id
            ).filter(Wishlist.user_id == current_user.id).scalar() or 0
            return {'wishlist_total_count': count}
        return {'wishlist_total_count': 0}

    @app.route('/')
    def index():
        from app.models import Listing, User
        from sqlalchemy import func

        recent_listings = (Listing.query
                           .filter_by(is_active=True, is_removed=False)
                           .order_by(Listing.created_at.desc())
                           .limit(8).all())

        category_counts_raw = (db.session.query(Listing.category, func.count(Listing.id))
                               .filter(Listing.is_active == True, Listing.is_removed == False)
                               .group_by(Listing.category).all())
        category_counts = {cat: count for cat, count in category_counts_raw}

        total_listings = Listing.query.filter_by(is_active=True, is_removed=False).count()
        total_users    = User.query.count()

        events = [
            {'title': 'O-Week Market Day',        'organizer': 'UWA Student Guild',         'date_day': '28', 'date_mon': 'Apr', 'location': 'Oak Lawn',             'icon': 'bi-balloon-heart'},
            {'title': 'CS Study Swap',             'organizer': 'UWA Computing Society',     'date_day': '3',  'date_mon': 'May', 'location': 'Reid Library Level 2', 'icon': 'bi-laptop'},
            {'title': 'Textbook Exchange',         'organizer': 'UWA Academic Association',  'date_day': '10', 'date_mon': 'May', 'location': 'Winthrop Hall Foyer',  'icon': 'bi-book'},
            {'title': 'End-of-Semester Clear-Out', 'organizer': 'UWA Residential Colleges',  'date_day': '31', 'date_mon': 'May', 'location': 'UniHall Common Room',  'icon': 'bi-house-heart'},
        ]

        sponsors = [
            {'name': 'UWA Student Guild',  'tagline': 'Your student union since 1913',    'icon': 'bi-mortarboard',      'url': '#'},
            {'name': 'UniPrint',           'tagline': 'Fast, affordable campus printing', 'icon': 'bi-printer',          'url': '#'},
            {'name': 'Campus Books Co-op', 'tagline': 'Buy & sell textbooks on campus',   'icon': 'bi-journal-bookmark', 'url': '#'},
        ]

        return render_template('home.html',
            recent_listings=recent_listings,
            category_counts=category_counts,
            total_listings=total_listings,
            total_users=total_users,
            events=events,
            sponsors=sponsors,
        )

    return app