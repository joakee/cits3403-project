from datetime import timedelta
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from config import Config

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

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(listings_bp)

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
        if current_user.is_authenticated:
            return redirect(url_for('listings.index'))
        return redirect(url_for('auth.login'))

    return app