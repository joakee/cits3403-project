from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


wishlist_items = db.Table('wishlist_items',
    db.Column('wishlist_id', db.Integer, db.ForeignKey('wishlist.id'), primary_key=True),
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.id'), primary_key=True)
)

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # A wishlist belongs to a user
    user = db.relationship('User', backref=db.backref('wishlists', lazy='dynamic'))

    # A wishlist contains many listings
    listings = db.relationship('Listing', secondary=wishlist_items, lazy='dynamic', backref=db.backref('saved_in_wishlists', lazy='dynamic'))

    def __repr__(self):
        return f'<Wishlist {self.name}>'



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text, default='')
    avatar_url = db.Column(db.String(256), nullable=True)

    listings = db.relationship('Listing', backref='seller', lazy='dynamic')

    def has_saved(self, listing):
        return db.session.query(wishlist_items).join(Wishlist).filter(Wishlist.user_id == self.id, wishlist_items.c.listing_id == listing.id).first() is not None

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

    @property
    def save_count(self):
        return db.session.query(Wishlist.user_id).join(wishlist_items).filter(wishlist_items.c.listing_id == self.id).distinct().count()

    @property
    def price_change_info(self):
        """Return dict {original, current, dropped} if price has changed via edit history, else None."""
        first_price_edit = ListingEdit.query.filter_by(
            listing_id=self.id, field_name='price'
        ).order_by(ListingEdit.edited_at.asc()).first()
        if first_price_edit:
            try:
                original = float(first_price_edit.old_value)
                current = float(self.price)
                if abs(original - current) > 0.001:
                    return {'original': original, 'current': current, 'dropped': current < original}
            except (ValueError, TypeError):
                pass
        return None

    edits = db.relationship(
        'ListingEdit',
        backref='listing',
        lazy='dynamic',
        order_by='ListingEdit.edited_at.desc()'
    )

    def __repr__(self):
        return f'<Listing {self.title}>'


class ListingEdit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow)
    field_name = db.Column(db.String(64), nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<ListingEdit {self.listing_id} {self.field_name}>'

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship('Message', backref='conversation', lazy='dynamic')
    listing = db.relationship('Listing', backref='conversations')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

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