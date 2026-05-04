from app import create_app, db
from app.models import User, Listing, ListingEdit
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 1. Create users
    print("Creating users...")
    u1 = User.query.filter_by(username='alice').first()
    if not u1:
        u1 = User(
            username='alice',
            email='alice@example.com',
            password_hash=generate_password_hash('password123', method='pbkdf2:sha256')
        )
        db.session.add(u1)
        
    u2 = User.query.filter_by(username='bob').first()
    if not u2:
        u2 = User(
            username='bob',
            email='bob@example.com',
            password_hash=generate_password_hash('password123', method='pbkdf2:sha256')
        )
        db.session.add(u2)

    u4 = User.query.filter_by(username='admin').first()
    if not u4:
        u4 = User(
            username='admin',
            email='admin@admin.com',
            password_hash=generate_password_hash('password123', method='pbkdf2:sha256'),
            is_admin=True
        )
        db.session.add(u4)

    db.session.commit()

    # 2. Create listings
    print("Creating listings...")
    l1 = Listing(
        title='Used Bicycle',
        description='A very nice used bicycle. Some scratches but rides well.',
        price=150.0,
        category='sports',
        seller_id=u1.id,
        is_active=True
    )
    
    l2 = Listing(
        title='Calculus Textbook',
        description='MAT101 textbook in good condition. Includes unused access code.',
        price=40.0,
        category='books',
        seller_id=u1.id,
        is_active=True
    )

    l3 = Listing(
        title='Gaming Laptop',
        description='Works great, runs all modern games. Comes with charger.',
        price=850.0,
        category='electronics',
        seller_id=u2.id,
        is_active=True
    )

    db.session.add_all([l1, l2, l3])
    db.session.commit()

    # 3. Create listing histories (Alice edits her listings)
    print("Creating edit history...")
    edit1 = ListingEdit(
        listing_id=l1.id,
        field_name='price',
        old_value='200.0',
        new_value='150.0'
    )
    
    edit2 = ListingEdit(
        listing_id=l1.id,
        field_name='description',
        old_value='A used bicycle.',
        new_value='A very nice used bicycle. Some scratches but rides well.'
    )

    edit3 = ListingEdit(
        listing_id=l2.id,
        field_name='title',
        old_value='Math Textbook',
        new_value='Calculus Textbook'
    )

    # Bob edits his listing
    edit4 = ListingEdit(
        listing_id=l3.id,
        field_name='price',
        old_value='1000.0',
        new_value='850.0'
    )

    db.session.add_all([edit1, edit2, edit3, edit4])
    db.session.commit()
    
    # 4. Add items to wishlist
    print("Adding items to wishlists...")
    u1.wishlist_listings.append(l3) # Alice wants Bob's laptop
    u2.wishlist_listings.append(l1) # Bob wants Alice's bike
    db.session.commit()

    print("Database seeded successfully with test users, listings, history, and wishlists.")
    print("User: alice@example.com / password123")
    print("User: bob@example.com / password123")
