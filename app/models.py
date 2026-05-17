from datetime import datetime, timedelta
from flask_login import UserMixin
from app import db, login_manager
import random


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user and not user.is_active:
        return None
    return user


wishlist_items = db.Table(
    'wishlist_items',
    db.Column('wishlist_id', db.Integer, db.ForeignKey('wishlist.id'), primary_key=True),
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.id'), primary_key=True)
)

store_follows = db.Table(
    'store_follows',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('store_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('wishlists', lazy='dynamic'))

    # A wishlist contains many listings
    listings = db.relationship(
        'Listing',
        secondary=wishlist_items,
        lazy='dynamic',
        backref=db.backref('saved_in_wishlists', lazy='dynamic')
    )

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
    is_admin = db.Column(db.Boolean, default=False)
    is_moderator = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    is_verified = db.Column(db.Boolean, default=False)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)

    microsoft_sub = db.Column(db.String(128), unique=True, nullable=True, index=True)

    banned_at = db.Column(db.DateTime, nullable=True)
    ban_reason = db.Column(db.Text, nullable=True)

    is_store = db.Column(db.Boolean, default=False)
    store_name = db.Column(db.String(128), nullable=True)
    store_address = db.Column(db.String(256), nullable=True)
    contact_phone = db.Column(db.String(32), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    store_bio = db.Column(db.Text, default='')

    listings = db.relationship(
        'Listing',
        backref='seller',
        lazy='dynamic',
        foreign_keys='Listing.seller_id'
    )

    following_stores = db.relationship(
        'User',
        secondary=store_follows,
        primaryjoin='User.id == store_follows.c.follower_id',
        secondaryjoin='User.id == store_follows.c.store_id',
        backref=db.backref('store_followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def generate_otp(self):
        self.otp_code = f"{random.randint(100000, 999999)}"
        self.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        return self.otp_code

    def has_saved(self, listing):
        return db.session.query(wishlist_items).join(Wishlist).filter(
            Wishlist.user_id == self.id,
            wishlist_items.c.listing_id == listing.id
        ).first() is not None

    def is_following_store(self, store_user):
        return self.following_stores.filter(
            store_follows.c.store_id == store_user.id
        ).count() > 0

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

    # Seller data / analytics
    view_count = db.Column(db.Integer, default=0)

    # Moderation/removal fields
    is_removed = db.Column(db.Boolean, default=False)
    removed_at = db.Column(db.DateTime, nullable=True)
    removed_reason = db.Column(db.Text, nullable=True)
    removed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    show_history = db.Column(db.Boolean, default=True)
    stock_quantity = db.Column(db.Integer, nullable=True)
    posted_as_store = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def save_count(self):
        return db.session.query(Wishlist.user_id).join(wishlist_items).filter(
            wishlist_items.c.listing_id == self.id
        ).distinct().count()

    @property
    def price_change_info(self):
        """Return dict {original, current, dropped} if price has changed via edit history, else None."""
        first_price_edit = ListingEdit.query.filter_by(
            listing_id=self.id,
            field_name='price'
        ).order_by(ListingEdit.edited_at.asc()).first()

        if first_price_edit:
            try:
                original = float(first_price_edit.old_value)
                current = float(self.price)

                if abs(original - current) > 0.001:
                    return {
                        'original': original,
                        'current': current,
                        'dropped': current < original
                    }
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


class ListingImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    image_url = db.Column(db.String(256), nullable=False)
    order = db.Column(db.Integer, default=0)

    listing = db.relationship('Listing', backref=db.backref('images', lazy='dynamic', order_by='ListingImage.order'))


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

    # Save message time in UTC.
    # chat.py converts this to AWST/Perth time for display.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    is_read = db.Column(db.Boolean, default=False)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reply_text = db.Column(db.Text, nullable=True)
    reply_at = db.Column(db.DateTime, nullable=True)

    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    reviewer = db.relationship(
        'User',
        foreign_keys=[reviewer_id],
        backref='reviews_written'
    )

    reviewed_user = db.relationship(
        'User',
        foreign_keys=[reviewed_user_id],
        backref='reviews_received'
    )

    def __repr__(self):
        return f'<Review {self.rating}/5 by {self.reviewer_id} for {self.reviewed_user_id}>'


class ListingView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    listing = db.relationship('Listing', backref='views')


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='open', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    handled_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    admin_note = db.Column(db.Text, nullable=True)

    reporter = db.relationship(
        'User',
        foreign_keys=[reporter_id],
        backref='reports_filed'
    )

    handled_by = db.relationship(
        'User',
        foreign_keys=[handled_by_id],
        backref='reports_handled'
    )

    REASON_CHOICES = [
        ('spam', 'Spam or misleading'),
        ('prohibited', 'Prohibited item'),
        ('scam', 'Suspected scam'),
        ('inappropriate', 'Inappropriate content'),
        ('duplicate', 'Duplicate listing'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = ['open', 'under_review', 'resolved', 'dismissed']

    @property
    def target(self):
        if self.target_type == 'listing':
            return Listing.query.get(self.target_id)
        elif self.target_type == 'user':
            return User.query.get(self.target_id)
        return None

    def __repr__(self):
        return f'<Report #{self.id} {self.target_type}:{self.target_id} [{self.status}]>'