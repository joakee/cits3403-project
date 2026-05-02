from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


wishlist_items = db.Table('wishlist_items',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text, default='')
    avatar_url = db.Column(db.String(256), nullable=True)

    listings = db.relationship('Listing', backref='seller', lazy='dynamic')
    wishlist_listings = db.relationship('Listing', secondary=wishlist_items, lazy='dynamic', backref=db.backref('wishlisted_by', lazy='dynamic'))

    def __repr__(self):
        return f'<User {self.username}>'


class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    image_url = db.Column(db.String(256), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    show_history = db.Column(db.Boolean, default=True)   # seller can hide edit history
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    edits = db.relationship(
        'ListingEdit',
        backref='listing',
        lazy='dynamic',
        order_by='ListingEdit.edited_at.desc()'
    )

    def __repr__(self):
        return f'<Listing {self.title}>'


class ListingEdit(db.Model):
    """One row per save; records a single changed field."""
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow)
    field_name = db.Column(db.String(64), nullable=False)   # e.g. 'title', 'price'
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<ListingEdit {self.listing_id} {self.field_name}>'


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviews_written')
    reviewed_user = db.relationship('User', foreign_keys=[reviewed_user_id], backref='reviews_received')

    def __repr__(self):
        return f'<Review {self.rating}/5 by {self.reviewer_id} for {self.reviewed_user_id}>'