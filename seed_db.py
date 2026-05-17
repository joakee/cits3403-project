#!/usr/bin/env python3

from app import create_app, db
from app.models import User, Listing, ListingEdit, Wishlist
from werkzeug.security import generate_password_hash

app = create_app()

PW = generate_password_hash('password123', method='pbkdf2:sha256')


def get_or_create_user(username, email, **kwargs):
    u = User.query.filter_by(username=username).first()
    if not u:
        u = User(username=username, email=email, password_hash=PW, **kwargs)
        db.session.add(u)
        db.session.flush()
    return u


with app.app_context():
    db.create_all()

    # ── Existing users ──────────────────────────────────────────────────────
    print("Creating users...")
    alice = get_or_create_user('alice', 'alice@example.com',
        bio='Selling stuff I no longer need. Based on campus.')
    bob = get_or_create_user('bob', 'bob@example.com',
        bio='Moderator and part-time seller.', is_moderator=True)
    admin = get_or_create_user('admin', 'admin@admin.com',
        bio='Site administrator.', is_admin=True)

    # ── Regular users ───────────────────────────────────────────────────────
    sarah  = get_or_create_user('sarah',   'sarah@example.com',   bio='First-year student clearing out my room.')
    james  = get_or_create_user('james',   'james@example.com',   bio='Selling textbooks after finishing my degree.')
    priya  = get_or_create_user('priya',   'priya@example.com',   bio='Love finding good deals and passing them on.')
    liam   = get_or_create_user('liam',    'liam@example.com',    bio='Moving out — everything must go!')
    mei    = get_or_create_user('mei',     'mei@example.com',     bio='PhD student selling old course materials.')
    omar   = get_or_create_user('omar',    'omar@example.com',    bio='Casual seller. All items in good condition.')
    chloe  = get_or_create_user('chloe',   'chloe@example.com',   bio='Fashion lover selling clothes I no longer wear.')
    ethan  = get_or_create_user('ethan',   'ethan@example.com',   bio='Tech enthusiast upgrading my setup.')
    sofia  = get_or_create_user('sofia',   'sofia@example.com',   bio='Interior design student selling furniture.')
    noah   = get_or_create_user('noah',    'noah@example.com',    bio='Selling sports gear after switching hobbies.')
    ava    = get_or_create_user('ava',     'ava@example.com',     bio='Minimalist — decluttering regularly.')
    marcus = get_or_create_user('marcus',  'marcus@example.com',  bio='Engineering student selling old lab gear.')
    lily   = get_or_create_user('lily',    'lily@example.com',    bio='Bookworm selling my finished reads.')
    ryan   = get_or_create_user('ryan',    'ryan@example.com',    bio='Gamer selling hardware upgrades.')
    zoe    = get_or_create_user('zoe',     'zoe@example.com',     bio='Art student selling supplies and prints.')
    dan    = get_or_create_user('dan',     'dan@example.com',     bio='Just trying to fund my next project.')
    jess   = get_or_create_user('jessica', 'jessica@example.com', bio='Selling clothes and accessories I bought but never wore.')
    tom    = get_or_create_user('tom',     'tom@example.com',     bio='Hobbyist seller — mainly electronics.')
    angela = get_or_create_user('angela',  'angela@example.com',  bio='Clearing out years of accumulated stuff.')
    sam    = get_or_create_user('sam',     'sam@example.com',     bio='Selling a bit of everything.')

    # ── Store accounts ──────────────────────────────────────────────────────
    techbazaar    = get_or_create_user('techbazaar',     'techbazaar@store.com',     bio='Your go-to store for quality refurbished electronics and accessories.', is_store=True, store_name='TechBazaar')
    bookshelf_co  = get_or_create_user('bookshelf_co',   'bookshelf@store.com',      bio='New and second-hand textbooks for all courses. Fast dispatch.',         is_store=True, store_name='Bookshelf Co.')
    campusgear    = get_or_create_user('campusgear',     'campusgear@store.com',     bio='Everything a student needs — stationery, bags, and study gear.',         is_store=True, store_name='Campus Gear')
    stylevault    = get_or_create_user('stylevault',     'stylevault@store.com',     bio='Curated second-hand fashion. New stock every week.',                     is_store=True, store_name='Style Vault')
    furnifinds    = get_or_create_user('furnifinds',     'furnifinds@store.com',     bio='Affordable pre-loved furniture. Perfect for student accommodation.',     is_store=True, store_name='FurniFinds')
    gadgetshop    = get_or_create_user('gadgetshop',     'gadgetshop@store.com',     bio='Gadgets, cables, and peripherals at unbeatable prices.',                 is_store=True, store_name='Gadget Shop')
    textbookdepot = get_or_create_user('textbookdepot',  'textbookdepot@store.com',  bio='Huge range of uni textbooks. All editions available.',                   is_store=True, store_name='Textbook Depot')
    sportzone     = get_or_create_user('sportzone',      'sportzone@store.com',      bio='Second-hand sports equipment for every sport and budget.',               is_store=True, store_name='Sport Zone')
    homehaven     = get_or_create_user('homehaven',      'homehaven@store.com',      bio='Homewares, kitchen items, and decor at student-friendly prices.',        is_store=True, store_name='Home Haven')
    nerdnook      = get_or_create_user('nerdnook',       'nerdnook@store.com',       bio='Collectibles, comics, board games, and all things nerdy.',               is_store=True, store_name='Nerd Nook')

    db.session.commit()

    # ── Listings ─────────────────────────────────────────────────────────────
    print("Creating listings...")

    def listing(title, desc, price, cat, seller, is_active=True, image_url=None, posted_as_store=False):
        l = Listing(title=title, description=desc, price=price,
                    category=cat, seller_id=seller.id, is_active=is_active, image_url=image_url,
                    posted_as_store=posted_as_store)
        db.session.add(l)
        return l

    # Alice
    l_alice1 = listing('Used Bicycle', 'A very nice used bicycle. Some scratches but rides well.', 150.0, 'other', alice)
    l_alice2 = listing('Calculus Textbook', 'MAT101 textbook in good condition. Includes unused access code.', 40.0, 'books', alice)

    # Bob
    l_bob1 = listing('Gaming Laptop', 'Works great, runs all modern games. Comes with charger.', 850.0, 'electronics', bob)

    # Sarah
    l_sarah1 = listing('Desk Lamp', 'Adjustable LED desk lamp, barely used.', 18.0, 'other', sarah)
    l_sarah2 = listing('Intro to Psychology', 'PSYC101 textbook, highlights on some pages.', 25.0, 'books', sarah)

    # James
    l_james1 = listing('Accounting Principles 3rd Ed', 'Good condition, no writing inside.', 55.0, 'books', james)
    l_james2 = listing('Formal Shirt (Size M)', 'Only worn twice. Navy blue.', 20.0, 'clothing', james)

    # Priya
    l_priya1 = listing('Wireless Mouse', 'Logitech M185. Works perfectly, batteries included.', 12.0, 'electronics', priya)

    # Liam
    l_liam1 = listing('Ikea Bed Frame (Single)', 'Good condition, missing two bolts but otherwise complete.', 60.0, 'furniture', liam)
    l_liam2 = listing('Mini Fridge', 'Perfect for dorm rooms. Cold and quiet.', 80.0, 'other', liam)
    l_liam3 = listing('Running Shoes (UK 10)', 'Nike Air, barely worn. Great condition.', 45.0, 'clothing', liam)

    # Mei
    l_mei1 = listing('Research Methods Textbook', 'Used one semester, very clean.', 30.0, 'books', mei)
    l_mei2 = listing('Laptop Stand', 'Adjustable aluminium stand. Pairs great with external keyboard.', 22.0, 'electronics', mei)

    # Omar
    l_omar1 = listing('Acoustic Guitar', 'Yamaha F310. Good beginner guitar with strap and picks.', 120.0, 'other', omar)

    # Chloe
    l_chloe1 = listing('Winter Coat (Size S)', 'Barely worn. Warm and stylish.', 35.0, 'clothing', chloe)
    l_chloe2 = listing('Denim Jacket (Size S)', 'Classic blue. Good condition.', 25.0, 'clothing', chloe)

    # Ethan
    l_ethan1 = listing('27" Monitor', 'LG 1080p. Works perfectly, minor scratch on bezel.', 180.0, 'electronics', ethan)
    l_ethan2 = listing('Mechanical Keyboard', 'Cherry MX Brown switches. Great typing feel.', 75.0, 'electronics', ethan)

    # Sofia
    l_sofia1 = listing('Coffee Table', 'Solid wood. Light wear on top surface.', 45.0, 'furniture', sofia)
    l_sofia2 = listing('Bookshelf (5 shelves)', 'White, flat-pack, fully assembled. No damage.', 30.0, 'furniture', sofia)

    # Noah
    l_noah1 = listing('Tennis Racket', 'Wilson Clash 100. Lightly used, includes cover.', 65.0, 'other', noah)

    # Ava
    l_ava1 = listing('Yoga Mat', 'Non-slip, 6mm thick. Used a few times.', 15.0, 'other', ava)

    # Marcus
    l_marcus1 = listing('Soldering Iron Kit', 'Complete kit with solder and tips. Great for electronics projects.', 28.0, 'electronics', marcus)
    l_marcus2 = listing('Circuit Analysis Textbook', 'Sadiku 5th Ed. Some pencil marks.', 45.0, 'books', marcus)

    # Lily
    l_lily1 = listing('The Name of the Wind', 'Paperback, great condition.', 8.0, 'books', lily)
    l_lily2 = listing('Atomic Habits', 'Lightly read. No markings.', 10.0, 'books', lily)

    # Ryan
    l_ryan1 = listing('PS5 Controller', 'White DualSense. Excellent condition.', 70.0, 'electronics', ryan)
    l_ryan2 = listing('Gaming Headset', 'HyperX Cloud II. Clear audio, mic works great.', 55.0, 'electronics', ryan)

    # Zoe
    l_zoe1 = listing('Acrylic Paint Set', 'Professional grade, 24 colours, barely used.', 20.0, 'other', zoe)

    # Dan
    l_dan1 = listing('Raspberry Pi 4 (4GB)', 'Complete kit with case and power supply.', 65.0, 'electronics', dan)

    # Jess
    l_jess1 = listing('Levi\'s Jeans (W28 L30)', 'Slim fit, dark wash. Excellent condition.', 30.0, 'clothing', jess)
    l_jess2 = listing('Handbag (Brown Leather)', 'Faux leather, like new.', 22.0, 'clothing', jess)

    # Tom
    l_tom1 = listing('USB-C Hub (7-in-1)', 'HDMI, USB 3.0, SD card, charging. Works perfectly.', 18.0, 'electronics', tom)
    l_tom2 = listing('Portable SSD 500GB', 'Samsung T7. Fast and compact.', 55.0, 'electronics', tom, is_active=False)

    # Angela
    l_angela1 = listing('Air Fryer', 'Philips 4.1L. Excellent condition, lightly used.', 60.0, 'other', angela)
    l_angela2 = listing('Dining Chairs x2', 'Matching set, solid wood. Minor scuffs.', 40.0, 'furniture', angela)

    # Sam
    l_sam1 = listing('Blender', 'Nutribullet 900W. All attachments included.', 35.0, 'other', sam)

    db.session.flush()

    # ── Store listings ───────────────────────────────────────────────────────

    # techbazaar
    listing('Refurbished iPhone 12', 'Unlocked, 64GB, 85% battery health. Includes charger.', 399.0, 'electronics', techbazaar, posted_as_store=True)
    listing('Refurbished MacBook Air (2020)', 'M1 chip, 8GB RAM, 256GB SSD. Excellent condition.', 849.0, 'electronics', techbazaar, posted_as_store=True)
    listing('iPad 9th Gen', '64GB WiFi. Screen protector applied. Good condition.', 280.0, 'electronics', techbazaar, posted_as_store=True)
    listing('AirPods Pro (Gen 1)', 'Noise cancelling. Case and tips included.', 140.0, 'electronics', techbazaar, posted_as_store=True)
    listing('Samsung Galaxy S22', '128GB, unlocked. Light wear on edges.', 320.0, 'electronics', techbazaar, posted_as_store=True)
    listing('Apple Watch SE', '40mm, GPS. Strap included.', 160.0, 'electronics', techbazaar, posted_as_store=True)

    # bookshelf_co
    listing('Fundamentals of Physics (Halliday)', '10th edition. Clean pages, no writing.', 65.0, 'books', bookshelf_co, posted_as_store=True)
    listing('Organic Chemistry (McMurry)', '9th edition. Good condition, minor highlighting.', 50.0, 'books', bookshelf_co, posted_as_store=True)
    listing('Introduction to Algorithms (CLRS)', '3rd edition. Light wear on cover.', 70.0, 'books', bookshelf_co, posted_as_store=True)
    listing('Human Anatomy & Physiology', '11th edition. Very clean.', 60.0, 'books', bookshelf_co, posted_as_store=True)
    listing('Principles of Economics (Mankiw)', '8th edition. Some highlighting.', 45.0, 'books', bookshelf_co, posted_as_store=True)
    listing('Data Structures and Algorithms in Python', 'First printing. No markings.', 55.0, 'books', bookshelf_co, posted_as_store=True)
    listing('Molecular Biology of the Cell', '6th edition. Excellent condition.', 68.0, 'books', bookshelf_co, posted_as_store=True)

    # campusgear
    listing('Laptop Backpack (30L)', 'Padded compartment, USB charging port. Black.', 35.0, 'other', campusgear, posted_as_store=True)
    listing('A4 Notebooks x5 Pack', 'Ruled, 200 pages each. Sealed.', 12.0, 'books', campusgear, posted_as_store=True)
    listing('Staedtler Pen Set', '12 fineliner pens. Various colours.', 9.0, 'other', campusgear, posted_as_store=True)
    listing('Graphing Calculator (Casio FX-9750)', 'Works perfectly. Batteries included.', 40.0, 'electronics', campusgear, posted_as_store=True)
    listing('Ergonomic Laptop Stand', 'Portable, adjustable height.', 25.0, 'electronics', campusgear, posted_as_store=True)

    # stylevault
    listing('Vintage Denim Jacket (M)', 'Light wash, 90s style. Great condition.', 38.0, 'clothing', stylevault, posted_as_store=True)
    listing('Floral Summer Dress (S)', 'Barely worn. Midi length.', 22.0, 'clothing', stylevault, posted_as_store=True)
    listing('Oversized Knit Sweater (L)', 'Cream colour. Very cosy.', 28.0, 'clothing', stylevault, posted_as_store=True)
    listing('Black Blazer (M)', 'Classic fit. Good condition.', 30.0, 'clothing', stylevault, posted_as_store=True)
    listing('Leather Boots (EU 38)', 'Genuine leather ankle boots. Minor wear on soles.', 55.0, 'clothing', stylevault, posted_as_store=True)
    listing('Linen Trousers (S)', 'Beige, wide-leg. Never worn.', 24.0, 'clothing', stylevault, posted_as_store=True)

    # furnifinds
    listing('Study Desk (100cm)', 'White MDF. Good condition, minor surface marks.', 55.0, 'furniture', furnifinds, posted_as_store=True)
    listing('Office Chair', 'Adjustable height, lumbar support. Black mesh.', 70.0, 'furniture', furnifinds, posted_as_store=True)
    listing('Wardrobe (2-door)', 'White. Requires flat-pack assembly. All parts present.', 80.0, 'furniture', furnifinds, posted_as_store=True)
    listing('Chest of Drawers (4-drawer)', 'Solid pine. Good condition.', 50.0, 'furniture', furnifinds, posted_as_store=True)
    listing('Bedside Table', 'Small with single drawer. White.', 20.0, 'furniture', furnifinds, posted_as_store=True)
    listing('Sofa (2-seater)', 'Grey fabric. Some wear on armrests.', 120.0, 'furniture', furnifinds, posted_as_store=True)

    # gadgetshop
    listing('HDMI Cable 2m (2-pack)', 'High-speed, 4K compatible.', 8.0, 'electronics', gadgetshop, posted_as_store=True)
    listing('USB-C Charging Cable (3-pack)', 'Braided nylon, 1m each.', 10.0, 'electronics', gadgetshop, posted_as_store=True)
    listing('Webcam 1080p', 'Plug and play, built-in mic. Works on all OS.', 30.0, 'electronics', gadgetshop, posted_as_store=True)
    listing('External Hard Drive 1TB', 'Western Digital. USB 3.0.', 48.0, 'electronics', gadgetshop, posted_as_store=True)
    listing('Portable Charger 20000mAh', 'Dual USB + USB-C output. Fast charge.', 28.0, 'electronics', gadgetshop, posted_as_store=True)

    # textbookdepot
    listing('Business Law (Nickolas James)', '4th edition. Minor highlighting.', 42.0, 'books', textbookdepot, posted_as_store=True)
    listing('Clinical Psychology (Barlow)', '9th edition. Good condition.', 58.0, 'books', textbookdepot, posted_as_store=True)
    listing('Environmental Science (Botkin)', '9th edition. Clean copy.', 52.0, 'books', textbookdepot, posted_as_store=True)
    listing('Financial Accounting (Weygandt)', '9th edition. Some pencil notes.', 48.0, 'books', textbookdepot, posted_as_store=True)
    listing('Sociology: The Core (Hughes)', '11th edition. No markings.', 38.0, 'books', textbookdepot, posted_as_store=True)

    # sportzone
    listing('Basketball', 'Wilson Evolution. Indoor/outdoor. Size 7.', 28.0, 'other', sportzone, posted_as_store=True)
    listing('Swim Goggles', 'Anti-fog, UV protection. One size fits most.', 12.0, 'other', sportzone, posted_as_store=True)
    listing('Jump Rope (Speed)', 'Adjustable length, ball bearings.', 9.0, 'other', sportzone, posted_as_store=True)
    listing('Resistance Bands Set', '5 levels, includes door anchor and handles.', 18.0, 'other', sportzone, posted_as_store=True)
    listing('Water Bottle 1L (Insulated)', 'Keeps cold 24h. Stainless steel.', 15.0, 'other', sportzone, posted_as_store=True)
    listing('Foam Roller', 'High density, 60cm. Good for recovery.', 16.0, 'other', sportzone, posted_as_store=True)

    # homehaven
    listing('Kettle (1.7L)', 'Russell Hobbs. Fast boil. Good condition.', 18.0, 'other', homehaven, posted_as_store=True)
    listing('Toaster (2-slice)', 'White. Works perfectly.', 12.0, 'other', homehaven, posted_as_store=True)
    listing('Duvet (Double, 10.5 tog)', 'Machine washable. Good condition.', 22.0, 'other', homehaven, posted_as_store=True)
    listing('Pillow Pair', 'Medium firmness. Clean.', 10.0, 'other', homehaven, posted_as_store=True)
    listing('Cutlery Set (16 piece)', 'Stainless steel. Complete set.', 14.0, 'other', homehaven, posted_as_store=True)
    listing('Plant Pot Set (3 sizes)', 'Terracotta-style ceramic. Good condition.', 12.0, 'other', homehaven, posted_as_store=True)

    # nerdnook
    listing('Catan Board Game', 'Complete set, all pieces present. Light wear on box.', 25.0, 'other', nerdnook, posted_as_store=True)
    listing('Magic: The Gathering Card Bundle', '200 mixed cards including rares.', 20.0, 'other', nerdnook, posted_as_store=True)
    listing('Funko Pop — Spider-Man', 'Unopened in box.', 14.0, 'other', nerdnook, posted_as_store=True)
    listing('Dungeons & Dragons Starter Set', 'Complete, lightly used once.', 18.0, 'other', nerdnook, posted_as_store=True)
    listing('Graphic Novel: Watchmen', 'Paperback. Good condition.', 10.0, 'other', nerdnook, posted_as_store=True)
    listing('Ticket to Ride (Europe)', 'Complete set. All cards and tokens present.', 30.0, 'other', nerdnook, image_url='/static/uploads/ticket_to_ride_europe.png', posted_as_store=True)

    db.session.commit()

    # ── Edit history ────────────────────────────────────────────────────────
    print("Creating edit history...")

    def add_edit(listing_obj, field, old_val, new_val):
        db.session.add(ListingEdit(
            listing_id=listing_obj.id,
            field_name=field,
            old_value=old_val,
            new_value=new_val
        ))

    add_edit(l_alice1, 'price', '200.0', '150.0')
    add_edit(l_alice1, 'description', 'A used bicycle.', 'A very nice used bicycle. Some scratches but rides well.')
    add_edit(l_alice2, 'title', 'Math Textbook', 'Calculus Textbook')
    add_edit(l_bob1,   'price', '1000.0', '850.0')
    add_edit(l_ethan1, 'price', '220.0', '180.0')
    add_edit(l_ethan1, 'description', 'LG 1080p monitor.', 'LG 1080p. Works perfectly, minor scratch on bezel.')
    add_edit(l_ryan1,  'price', '85.0', '70.0')
    add_edit(l_liam1,  'description', 'Ikea single bed frame.', 'Good condition, missing two bolts but otherwise complete.')

    db.session.commit()

    # ── Wishlists ───────────────────────────────────────────────────────────
    print("Creating wishlists...")

    def ensure_wishlist(user):
        wl = Wishlist.query.filter_by(user_id=user.id).first()
        if not wl:
            wl = Wishlist(name='Saved Items', user_id=user.id)
            db.session.add(wl)
            db.session.flush()
        return wl

    wl_alice  = ensure_wishlist(alice);  wl_alice.listings.append(l_bob1);    wl_alice.listings.append(l_ethan1)
    wl_bob    = ensure_wishlist(bob);    wl_bob.listings.append(l_alice1)
    wl_sarah  = ensure_wishlist(sarah);  wl_sarah.listings.append(l_mei2)
    wl_james  = ensure_wishlist(james);  wl_james.listings.append(l_ethan2)
    wl_priya  = ensure_wishlist(priya);  wl_priya.listings.append(l_alice2);   wl_priya.listings.append(l_marcus2)
    wl_liam   = ensure_wishlist(liam);   wl_liam.listings.append(l_ryan1)
    wl_mei    = ensure_wishlist(mei);    wl_mei.listings.append(l_dan1)
    wl_omar   = ensure_wishlist(omar);   wl_omar.listings.append(l_bob1)
    wl_chloe  = ensure_wishlist(chloe);  wl_chloe.listings.append(l_jess1)
    wl_ethan  = ensure_wishlist(ethan);  wl_ethan.listings.append(l_ryan2)
    wl_sofia  = ensure_wishlist(sofia);  wl_sofia.listings.append(l_angela2)
    wl_noah   = ensure_wishlist(noah);   wl_noah.listings.append(l_ava1)
    wl_ava    = ensure_wishlist(ava);    wl_ava.listings.append(l_alice1)
    wl_marcus = ensure_wishlist(marcus); wl_marcus.listings.append(l_dan1)
    wl_lily   = ensure_wishlist(lily);   wl_lily.listings.append(l_lily2)
    wl_ryan   = ensure_wishlist(ryan);   wl_ryan.listings.append(l_bob1)
    wl_zoe    = ensure_wishlist(zoe);    wl_zoe.listings.append(l_chloe1)
    wl_dan    = ensure_wishlist(dan);    wl_dan.listings.append(l_ethan1)
    wl_jess   = ensure_wishlist(jess);   wl_jess.listings.append(l_chloe2)
    wl_tom    = ensure_wishlist(tom);    wl_tom.listings.append(l_marcus1)
    wl_angela = ensure_wishlist(angela); wl_angela.listings.append(l_liam2)
    wl_sam    = ensure_wishlist(sam);    wl_sam.listings.append(l_angela1)

    db.session.commit()

    print("\nDatabase seeded successfully.")
    print("All accounts use password: password123")
    print("\nRegular users:")
    for name in ['alice', 'bob', 'sarah', 'james', 'priya', 'liam', 'mei', 'omar',
                 'chloe', 'ethan', 'sofia', 'noah', 'ava', 'marcus', 'lily', 'ryan',
                 'zoe', 'dan', 'jessica', 'tom', 'angela', 'sam']:
        print(f"  {name}@example.com")
    print("\nStore accounts:")
    for name in ['techbazaar', 'bookshelf_co', 'campusgear', 'stylevault', 'furnifinds',
                 'gadgetshop', 'textbookdepot', 'sportzone', 'homehaven', 'nerdnook']:
        print(f"  {name}@store.com")
    print("\nAdmin: admin@admin.com")
