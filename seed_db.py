#!/usr/bin/env python3

from app import create_app, db
import re
import os as _os
from app.models import User, Listing, ListingEdit, Wishlist, ListingImage
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

    # ── Additional regular users ─────────────────────────────────────────────
    finn   = get_or_create_user('finn',   'finn@example.com',   bio='Music student offloading gear between semesters.')
    grace  = get_or_create_user('grace',  'grace@example.com',  bio='Nursing student — selling textbooks and uniforms.')
    henry  = get_or_create_user('henry',  'henry@example.com',  bio='Law student clearing out after graduation.')
    isabel = get_or_create_user('isabel', 'isabel@example.com', bio='Exchange student — selling before I fly home.')
    jake   = get_or_create_user('jake',   'jake@example.com',   bio='Commerce student, good condition items only.')
    karen  = get_or_create_user('karen',  'karen@example.com',  bio='Mature-age student downsizing the kitchen.')
    leo    = get_or_create_user('leo',    'leo@example.com',    bio='Architecture student selling design tools.')
    mia    = get_or_create_user('mia',    'mia@example.com',    bio='Education student, craft supplies and books.')
    nina   = get_or_create_user('nina',   'nina@example.com',   bio='Science student offloading lab gear.')
    oliver = get_or_create_user('oliver', 'oliver@example.com', bio='Med student — too many textbooks, not enough shelf space.')
    pam    = get_or_create_user('pam',    'pam@example.com',    bio='Arts student selling prints and supplies.')
    quinn  = get_or_create_user('quinn',  'quinn@example.com',  bio='Enviro sci student, eco-friendly bits and pieces.')
    rob    = get_or_create_user('rob',    'rob@example.com',    bio='IT student upgrading my whole setup.')
    stella = get_or_create_user('stella', 'stella@example.com', bio='Psychology student, books and study gear.')
    travis = get_or_create_user('travis', 'travis@example.com', bio='Engineering student selling tools and textbooks.')
    uma    = get_or_create_user('uma',    'uma@example.com',    bio='International student selling before heading home.')
    victor = get_or_create_user('victor', 'victor@example.com', bio='History buff selling books and collectibles.')
    wendy  = get_or_create_user('wendy',  'wendy@example.com',  bio='Social work student, practical and affordable listings.')
    xavier = get_or_create_user('xavier', 'xavier@example.com', bio='Maths student with too many calculators.')
    yuki   = get_or_create_user('yuki',   'yuki@example.com',   bio='Selling Japanese stationery and kitchenware.')
    zach   = get_or_create_user('zach',   'zach@example.com',   bio='Sports science student upgrading gym gear.')
    anna   = get_or_create_user('anna',   'anna@example.com',   bio='Chemistry student, lab manuals and gear.')
    ben    = get_or_create_user('ben',    'ben@example.com',    bio='Econ student selling business essentials.')
    cara   = get_or_create_user('cara',   'cara@example.com',   bio='Criminology student, books and stationery.')
    derek  = get_or_create_user('derek',  'derek@example.com',  bio='Philosophy grad selling a lifetime of books.')
    elle   = get_or_create_user('elle',   'elle@example.com',   bio='Film student selling camera gear.')
    felix  = get_or_create_user('felix',  'felix@example.com',  bio='CS student selling tech I no longer use.')
    gina   = get_or_create_user('gina',   'gina@example.com',   bio='Marketing student, fashion and accessories.')
    harry  = get_or_create_user('harry',  'harry@example.com',  bio='Geology student, field gear and textbooks.')
    iris   = get_or_create_user('iris',   'iris@example.com',   bio='Linguistics student selling language books.')
    joel   = get_or_create_user('joel',   'joel@example.com',   bio='Accounting student, office supplies and books.')
    kate   = get_or_create_user('kate',   'kate@example.com',   bio='Biomedical student selling lab and study gear.')
    lance  = get_or_create_user('lance',  'lance@example.com',  bio='PE student selling sports equipment.')
    mona   = get_or_create_user('mona',   'mona@example.com',   bio='Politics student, books and debate prep.')
    ned    = get_or_create_user('ned',    'ned@example.com',    bio='Creative writing student — books, books, books.')
    opal   = get_or_create_user('opal',   'opal@example.com',   bio='Anthropology student with global finds.')
    pete   = get_or_create_user('pete',   'pete@example.com',   bio='Civil engineering student selling textbooks and tools.')
    rosa   = get_or_create_user('rosa',   'rosa@example.com',   bio='Design student selling art supplies and gear.')
    steve  = get_or_create_user('steve',  'steve@example.com',  bio='Marine science student, ocean gear for sale.')
    tara   = get_or_create_user('tara',   'tara@example.com',   bio='Music student selling instruments and theory books.')
    uri    = get_or_create_user('uri',    'uri@example.com',    bio='International relations student, well-read seller.')
    vera   = get_or_create_user('vera',   'vera@example.com',   bio='Sociology student decluttering between semesters.')
    will   = get_or_create_user('will',   'will@example.com',   bio='Agriculture student selling tools and outdoor gear.')
    xena   = get_or_create_user('xena',   'xena@example.com',   bio='Neuroscience student selling study materials.')

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

    # ── Additional user listings ─────────────────────────────────────────────

    # finn
    listing('Guitar Amplifier (15W)', 'Fender Frontman 15G. Great for practice. Minor tolex wear.', 90.0, 'other', finn)
    listing('Vinyl Record Collection (x12)', 'Mix of classic rock and jazz. All in sleeves, good condition.', 45.0, 'other', finn)
    listing('MIDI Keyboard (25-key)', 'Arturia MiniLab MKII. USB-powered. Barely used.', 60.0, 'electronics', finn)
    listing('Studio Headphones', 'Audio-Technica ATH-M20x. Flat response, great for mixing.', 50.0, 'electronics', finn)
    listing('Guitar Stand (x2)', 'Hercules folding stands. Sold as a pair.', 18.0, 'other', finn)

    # grace
    listing('Anatomy & Physiology (Marieb)', '11th ed. Some highlighting. Good condition.', 55.0, 'books', grace)
    listing('Nursing Uniform Set', 'Size 10. Two tops and one pair of pants. Worn twice.', 25.0, 'clothing', grace)
    listing('Clinical Skills for Nurses', 'Latest edition. Very clean copy.', 38.0, 'books', grace)
    listing('Stethoscope (3M Littmann)', 'Classic III. Navy blue. Excellent condition.', 80.0, 'other', grace)
    listing('Study Planner & Journal', 'Hardcover, undated. Barely used.', 10.0, 'other', grace)

    # henry
    listing('Australian Contract Law (Carter)', '5th ed. Pencil annotations throughout.', 60.0, 'books', henry)
    listing('Corporations Law (Lipton)', '16th ed. Good condition.', 55.0, 'books', henry)
    listing('Evidence (Ligertwood)', '5th ed. Minor highlights.', 48.0, 'books', henry)
    listing('Suit Jacket (Size 40R)', 'Navy blue, slim fit. Worn to moots only.', 45.0, 'clothing', henry)
    listing('Leather Portfolio Folder', 'A4. Professional look. Light scuff on corner.', 20.0, 'other', henry)

    # isabel
    listing('Canon EOS M50 (Body Only)', 'Great condition. Low shutter count. Includes battery and charger.', 420.0, 'electronics', isabel)
    listing('Universal Travel Adapter', 'Works in 150+ countries. USB-A and USB-C ports.', 15.0, 'electronics', isabel)
    listing('Japanese for Busy People (Vol 1–3)', 'Complete set. Some pencil notes.', 30.0, 'books', isabel)
    listing('Samsonite Cabin Bag (20")', 'Hard shell, spinner wheels. Minor scratch on shell.', 75.0, 'other', isabel)
    listing('Portable Neck Pillow', 'Memory foam. Good condition, includes carry bag.', 12.0, 'other', isabel)

    # jake
    listing('Principles of Marketing (Kotler)', '17th ed. Clean copy.', 50.0, 'books', jake)
    listing('Business Statistics (Selvanathan)', '6th ed. Minor highlighting.', 45.0, 'books', jake)
    listing('Slim Fit Suit (Size 38)', 'Charcoal grey. Two-piece. Excellent condition.', 80.0, 'clothing', jake)
    listing('Texas Instruments BA II Plus', 'Financial calculator. Works perfectly.', 28.0, 'electronics', jake)
    listing('White Dress Shirts x3 (Size M)', 'All good condition. Iron-free fabric.', 30.0, 'clothing', jake)

    # karen
    listing('KitchenAid Stand Mixer', '4.3L bowl. Comes with dough hook, whisk and paddle.', 180.0, 'other', karen)
    listing('Slow Cooker (6L)', 'Sunbeam. Three heat settings. Clean and working.', 30.0, 'other', karen)
    listing('Nespresso Machine', 'Vertuo Next. Includes milk frother. Great condition.', 95.0, 'other', karen)
    listing('Baking Tin Set (6 piece)', 'Various sizes. Non-stick. Light use.', 18.0, 'other', karen)
    listing('Cookbook Collection (x8)', 'Mix of baking and general cooking. All in good condition.', 25.0, 'books', karen)

    # leo
    listing('Wacom Intuos Drawing Tablet (M)', 'Bluetooth. Includes stylus and spare nibs.', 110.0, 'electronics', leo)
    listing('Architecture: Form, Space & Order', '4th ed. Good condition, minor cover wear.', 45.0, 'books', leo)
    listing('Rotring 600 Drafting Set', 'Includes compass, rulers and pencils. Excellent condition.', 55.0, 'other', leo)
    listing('Scale Model Making Kit', 'Balsa wood, adhesives, cutting mat. Partial use.', 22.0, 'other', leo)

    # mia
    listing('The Art of Teaching (4th ed)', 'Used one semester. Good condition.', 35.0, 'books', mia)
    listing('Craft Supply Bundle', 'Scissors, glue guns, foam sheets, pom poms. Large box.', 20.0, 'other', mia)
    listing('Classroom Timer (Digital)', 'Large display. Magnetic back. Works perfectly.', 12.0, 'other', mia)
    listing('Children\'s Picture Book Set (x15)', 'Mix of classics and new releases. All excellent condition.', 35.0, 'books', mia)

    # nina
    listing('Atkins\' Physical Chemistry', '11th ed. Some highlighting.', 60.0, 'books', nina)
    listing('Lab Coat (Size 10)', 'White, knee length. Used one semester.', 15.0, 'clothing', nina)
    listing('Safety Goggles (x2)', 'Clear lens, anti-fog. Never used.', 8.0, 'other', nina)
    listing('Casio FX-991EX Calculator', 'Advanced scientific. Works perfectly.', 22.0, 'electronics', nina)

    # oliver
    listing('Harrison\'s Principles of Internal Medicine', '20th ed. Heavy but comprehensive. Good condition.', 90.0, 'books', oliver)
    listing('Oxford Handbook of Clinical Medicine', '10th ed. Pocket-sized. Lightly annotated.', 35.0, 'books', oliver)
    listing('Medical Scrubs Set (Size M)', 'Navy blue. Two sets. Washed and clean.', 28.0, 'clothing', oliver)
    listing('Littmann Cardiology IV Stethoscope', 'Black finish. Excellent condition.', 140.0, 'other', oliver)

    # pam
    listing('Winsor & Newton Oil Paint Set', '24 tubes, half used. With two brushes.', 30.0, 'other', pam)
    listing('A2 Canvas Prints (x3)', 'Original artworks. Abstract style. Framed.', 40.0, 'other', pam)
    listing('Art History: A Very Short Introduction', 'Paperback. Good condition.', 8.0, 'books', pam)
    listing('Easel (Wooden, Tabletop)', 'Foldable. Good condition.', 20.0, 'other', pam)

    # quinn
    listing('Environmental Science (Botkin & Keller)', '9th ed. Some pencil notes.', 48.0, 'books', quinn)
    listing('Reusable Water Bottles (x4)', 'Assorted sizes. BPA-free. All clean.', 16.0, 'other', quinn)
    listing('Hiking Daypack (20L)', 'Osprey Daylite. Good condition, minor fading.', 45.0, 'other', quinn)
    listing('Field Identification Guide: Australian Birds', 'Paperback. Well-loved.', 12.0, 'books', quinn)

    # rob
    listing('Second Monitor (24" FHD)', 'LG 24MK430H. Good condition, no dead pixels.', 130.0, 'electronics', rob)
    listing('Mechanical Keyboard (TKL)', 'Keychron K2. Gateron Red switches. Excellent condition.', 90.0, 'electronics', rob)
    listing('Logitech MX Master 3 Mouse', 'Works perfectly. Minor wear on grip.', 55.0, 'electronics', rob)
    listing('Introduction to Networking (Tanenbaum)', '6th ed. Good condition.', 50.0, 'books', rob)

    # stella
    listing('Abnormal Psychology (Barlow)', '9th ed. Highlighting throughout.', 45.0, 'books', stella)
    listing('Research Methods in Psychology (Gravetter)', '10th ed. Clean copy.', 50.0, 'books', stella)
    listing('Therapy Journal (Blank)', 'A5 hardcover, 200 pages. Barely used.', 10.0, 'other', stella)
    listing('LED Reading Lamp', 'USB rechargeable. Three brightness levels.', 14.0, 'electronics', stella)

    # travis
    listing('Engineering Mechanics: Statics (Hibbeler)', '14th ed. Good condition.', 55.0, 'books', travis)
    listing('Multimeter (Digital)', 'Fluke 115. Professional grade. Works perfectly.', 65.0, 'electronics', travis)
    listing('Steel-cap Safety Boots (UK 9)', 'Blundstone 991. Good condition.', 55.0, 'clothing', travis)
    listing('Hard Hat (White)', 'Never used on site. Adjustable.', 12.0, 'other', travis)
    listing('Thermodynamics: An Engineering Approach', '8th ed. Annotated lightly.', 50.0, 'books', travis)

    # uma
    listing('Rice Cooker (1.8L)', 'Zojirushi NS-TSC10. Excellent condition.', 55.0, 'other', uma)
    listing('Traditional Salwar Kameez (Size S)', 'Silk blend. Gold embroidery. Worn once.', 35.0, 'clothing', uma)
    listing('Learn Hindi in 30 Days', 'Paperback workbook. Some completed exercises.', 8.0, 'books', uma)
    listing('Tiffin Lunchbox (3-tier)', 'Stainless steel. Good condition.', 15.0, 'other', uma)

    # victor
    listing('A History of the Modern World (Palmer)', '10th ed. Good condition.', 30.0, 'books', victor)
    listing('The Guns of August (Tuchman)', 'Paperback. Good condition.', 10.0, 'books', victor)
    listing('Decorative World Globe (30cm)', 'Antique-style finish. Good condition.', 35.0, 'other', victor)
    listing('Oxford Dictionary of World History', 'Hardcover. Excellent condition.', 20.0, 'books', victor)

    # wendy
    listing('Social Work: An Introduction (Horner)', '3rd ed. Some highlighting.', 38.0, 'books', wendy)
    listing('Tote Bag (Canvas, x2)', 'One natural, one black. Good condition.', 12.0, 'other', wendy)
    listing('Motivational Desk Planner', 'Undated. Hardcover. Barely used.', 8.0, 'other', wendy)

    # xavier
    listing('Calculus (Stewart)', '8th ed. Pencil marks in first few chapters.', 55.0, 'books', xavier)
    listing('Linear Algebra Done Right (Axler)', '3rd ed. Excellent condition.', 42.0, 'books', xavier)
    listing('HP Prime Graphing Calculator', 'Touch screen. Works perfectly.', 70.0, 'electronics', xavier)
    listing('Graph Paper Notebook (x3)', 'A4, spiral-bound. Barely used.', 10.0, 'other', xavier)

    # yuki
    listing('Japanese Tea Set (5-piece)', 'Ceramic. Minor chip on one lid. Excellent otherwise.', 28.0, 'other', yuki)
    listing('Calligraphy Brush Set', '12 brushes, various sizes. Lightly used.', 18.0, 'other', yuki)
    listing('Japanese Cookbook: Washoku', 'Hardcover. Excellent condition.', 15.0, 'books', yuki)
    listing('Kokuyo Campus Notebooks (x10)', 'B5 ruled. Unopened pack.', 12.0, 'other', yuki)

    # zach
    listing('Adjustable Dumbbell Set (2–24kg)', 'Bowflex SelectTech. Excellent condition.', 180.0, 'other', zach)
    listing('Foam Yoga Mat (10mm)', 'Extra thick. Purple. Good condition.', 18.0, 'other', zach)
    listing('Nike Running Shoes (UK 11)', 'Pegasus 39. Used twice. Like new.', 80.0, 'clothing', zach)
    listing('Gym Bag (Large)', 'Under Armour Undeniable 5.0. Good condition.', 25.0, 'other', zach)
    listing('Resistance Band Set (Heavy)', 'Set of 5 loop bands. Barely used.', 14.0, 'other', zach)

    # anna
    listing('Organic Chemistry (Clayden)', '2nd ed. Clean copy, minor cover scuff.', 70.0, 'books', anna)
    listing('Chemistry Lab Manual (UWA)', 'Filled in partially. Good reference.', 12.0, 'books', anna)
    listing('Periodic Table Poster (A1)', 'Laminated. Good condition.', 8.0, 'other', anna)

    # ben
    listing('Economics (Samuelson & Nordhaus)', '19th ed. Some highlighting.', 40.0, 'books', ben)
    listing('Financial Times Subscription (3 months)', 'Unused digital code.', 25.0, 'other', ben)
    listing('Business Casual Shirts (x4, Size M)', 'Mix of colours. Good condition.', 35.0, 'clothing', ben)
    listing('Scientific Calculator (Casio FX-100AU)', 'Works perfectly. Includes manual.', 15.0, 'electronics', ben)

    # cara
    listing('Criminology: A Sociological Introduction (Carrabine)', '3rd ed. Good condition.', 38.0, 'books', cara)
    listing('True Crime Paperback Bundle (x5)', 'Mix of popular titles. All good condition.', 20.0, 'books', cara)
    listing('Insulated Travel Mug (500ml)', 'KeepCup. Good condition, no leaks.', 14.0, 'other', cara)

    # derek
    listing('Being and Time (Heidegger)', 'Paperback translation. Well-read.', 15.0, 'books', derek)
    listing('The Problems of Philosophy (Russell)', 'Paperback. Good condition.', 8.0, 'books', derek)
    listing('Vintage Vinyl Records (x8)', 'Classical and jazz. All in sleeves.', 30.0, 'other', derek)

    # elle
    listing('Canon AE-1 Film Camera', 'Working condition. Light seals replaced. Includes 50mm lens.', 160.0, 'electronics', elle)
    listing('Fujifilm Instax Mini 11', 'Blush pink. Works perfectly. Includes 10 shots.', 55.0, 'electronics', elle)
    listing('Understanding Exposure (Peterson)', '4th ed. Good condition.', 18.0, 'books', elle)
    listing('Colour Negative Film (5 rolls)', 'Kodak Ultramax 400. Unopened.', 30.0, 'other', elle)

    # felix
    listing('Clean Code (Robert C. Martin)', 'Paperback. Light highlighting.', 25.0, 'books', felix)
    listing('Raspberry Pi 4 Starter Kit', '4GB RAM. Includes case, SD card and power supply.', 70.0, 'electronics', felix)
    listing('RGB Gaming Mouse', 'Razer DeathAdder V2. Excellent condition.', 45.0, 'electronics', felix)
    listing('27" 144Hz Gaming Monitor', 'MSI Optix G27C4. Good condition.', 200.0, 'electronics', felix)

    # gina
    listing('Marketing Management (Kotler & Keller)', '15th ed. Good condition.', 48.0, 'books', gina)
    listing('Crossbody Bag (Tan Leather)', 'Genuine leather. Good condition.', 40.0, 'clothing', gina)
    listing('Fashion Magazines Bundle (x20)', 'Vogue and Harper\'s Bazaar. Various issues.', 15.0, 'other', gina)

    # harry
    listing('Mineralogy (Nesse)', '3rd ed. Minor highlights.', 50.0, 'books', harry)
    listing('Estwing Rock Hammer', 'Geology pick. Excellent condition.', 35.0, 'other', harry)
    listing('Hand Lens 10x Loupe', 'Geologist\'s loupe. Good condition.', 12.0, 'other', harry)
    listing('Hiking Boots (UK 10)', 'Merrell Moab 2. Good condition, resoled once.', 60.0, 'clothing', harry)

    # iris
    listing('Linguistics: An Introduction (Fromkin)', '3rd ed. Clean copy.', 40.0, 'books', iris)
    listing('Spanish-English Dictionary (Oxford)', 'Pocket edition. Good condition.', 8.0, 'books', iris)
    listing('A5 Language Notebooks (x6)', 'Lined, used for vocab practice.', 6.0, 'other', iris)

    # joel
    listing('Financial Accounting (Weygandt)', '9th ed. Pencil notes, erasable.', 48.0, 'books', joel)
    listing('Cost Accounting (Horngren)', '15th ed. Good condition.', 52.0, 'books', joel)
    listing('Desk Organiser Set', 'Bamboo, 5-piece. Good condition.', 14.0, 'other', joel)
    listing('Stapler & Hole Punch Combo', 'Both working. Good condition.', 10.0, 'other', joel)

    # kate
    listing('Molecular Cell Biology (Lodish)', '8th ed. Good condition.', 75.0, 'books', kate)
    listing('Student Microscope', 'AmScope 40x–1000x. Excellent condition, includes slides.', 85.0, 'electronics', kate)
    listing('Dissection Kit', 'Complete set, stainless steel. Used twice.', 18.0, 'other', kate)
    listing('Lab Safety Goggles', 'Indirect vent. Brand new.', 7.0, 'other', kate)

    # lance
    listing('Cricket Bat (Grade 1)', 'Gray-Nicolls Kaboom. Good condition, lightly oiled.', 70.0, 'other', lance)
    listing('Tennis Racket (Head Speed)', 'Good condition, restrung last month.', 60.0, 'other', lance)
    listing('Gym Backpack', 'Adidas. Multiple compartments. Good condition.', 22.0, 'other', lance)
    listing('Whey Protein Powder (1kg)', 'Chocolate flavour. 80% remaining.', 30.0, 'other', lance)

    # mona
    listing('Politics Among Nations (Morgenthau)', '7th ed. Good condition.', 35.0, 'books', mona)
    listing('The Prince (Machiavelli)', 'Penguin Classic. Good condition.', 8.0, 'books', mona)
    listing('Debate Prep Binder', 'Includes notes and argument templates. Handwritten.', 10.0, 'other', mona)

    # ned
    listing('On Writing (Stephen King)', 'Paperback. Excellent condition.', 12.0, 'books', ned)
    listing('Bird by Bird (Anne Lamott)', 'Paperback. Good condition.', 10.0, 'books', ned)
    listing('Leuchtturm1917 Notebook (A5)', 'Dotted. 80% blank pages remaining.', 14.0, 'other', ned)
    listing('Vintage Desk Lamp', 'Brass finish. Works perfectly. Great aesthetic.', 30.0, 'other', ned)

    # opal
    listing('Cultural Anthropology (Kottak)', '15th ed. Minor highlights.', 42.0, 'books', opal)
    listing('Passport Holder & Travel Wallet', 'Genuine leather. Good condition.', 18.0, 'other', opal)
    listing('Woven Wall Hanging', 'Boho style, 60cm wide. Good condition.', 20.0, 'other', opal)

    # pete
    listing('Structural Analysis (Hibbeler)', '10th ed. Pencil notes.', 55.0, 'books', pete)
    listing('AutoCAD 2023 (Student License)', 'Unused code. Single-use.', 30.0, 'electronics', pete)
    listing('Construction Hard Hat (Yellow)', 'Barely used. Adjustable.', 10.0, 'other', pete)
    listing('Steel Rule & Spirit Level Set', 'Good condition. Accurate.', 15.0, 'other', pete)

    # rosa
    listing('Graphic Design: The New Basics (Lupton)', '2nd ed. Good condition.', 38.0, 'books', rosa)
    listing('Sketchbook Bundle (A3, x3)', 'Hardcover. All partially used.', 18.0, 'other', rosa)
    listing('Wacom Bamboo Sketch Stylus', 'For iPad. Works perfectly.', 28.0, 'electronics', rosa)
    listing('Acrylic & Gouache Paint Set', 'Professional grade. Lightly used.', 22.0, 'other', rosa)

    # steve
    listing('Marine Biology (Castro & Huber)', '9th ed. Good condition.', 52.0, 'books', steve)
    listing('Snorkelling Set', 'Mask, snorkel and fins (size M). Good condition.', 35.0, 'other', steve)
    listing('3mm Wetsuit (Size M)', 'O\'Neill. Good condition, no tears.', 55.0, 'clothing', steve)

    # tara
    listing('3/4 Violin (Stentor Student II)', 'Good condition. Includes bow and case.', 85.0, 'other', tara)
    listing('Music Theory in Practice (Grade 4)', 'ABRSM. Some completed exercises.', 10.0, 'books', tara)
    listing('Sheet Music Bundle (Classical)', '20+ pieces. Various composers.', 18.0, 'other', tara)
    listing('Clip-on Tuner & Metronome', 'Snark SN-5. Works perfectly.', 12.0, 'electronics', tara)

    # uri
    listing('International Relations (Baylis & Smith)', '6th ed. Good condition.', 44.0, 'books', uri)
    listing('World Atlas (National Geographic)', 'Large format. Good condition.', 22.0, 'books', uri)
    listing('Leather Passport Holder', 'Brown. Good condition.', 12.0, 'other', uri)

    # vera
    listing('Sociology: A Global Introduction (Macionis)', '6th ed. Minor highlights.', 40.0, 'books', vera)
    listing('The Sociological Imagination (Mills)', 'Paperback. Good condition.', 10.0, 'books', vera)
    listing('Compact Reading Glasses (+1.5)', 'Foldable frame. Good condition.', 8.0, 'other', vera)

    # will
    listing('Introduction to Agriculture (Christensen)', '3rd ed. Good condition.', 38.0, 'books', will)
    listing('Garden Trowel & Fork Set', 'Stainless steel. Good condition.', 14.0, 'other', will)
    listing('Rubber Boots (UK 9)', 'Green. Good condition.', 22.0, 'clothing', will)

    # xena
    listing('Principles of Neural Science (Kandel)', '5th ed. Heavy but comprehensive. Good condition.', 85.0, 'books', xena)
    listing('Brain Anatomy Model (Resin)', 'Labelled, 8-part. Good condition.', 40.0, 'other', xena)
    listing('Cognitive Neuroscience (Gazzaniga)', '5th ed. Some highlighting.', 58.0, 'books', xena)

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

    # ── Wire up images ──────────────────────────────────────────────────────
    print("Wiring up images...")
    upload_folder = _os.path.join(app.root_path, 'static', 'uploads')
    primary = {}   # listing_id -> url  (from _fb.jpg)
    gallery = {}   # listing_id -> list of (order, url)  (from _fb_N.jpg)

    for fname in _os.listdir(upload_folder):
        m = re.match(r'.+?_(\d+)_fb(_(\d+))?\.jpg$', fname)
        if not m:
            continue
        lid = int(m.group(1))
        if m.group(2) is None:
            primary[lid] = f'/static/uploads/{fname}'
        else:
            gallery.setdefault(lid, []).append((int(m.group(3)), f'/static/uploads/{fname}'))

    for lid, url in primary.items():
        l = db.session.get(Listing, lid)
        if l:
            l.image_url = url

    for lid, imgs in gallery.items():
        l = db.session.get(Listing, lid)
        if not l:
            continue
        for idx, url in sorted(imgs):
            db.session.add(ListingImage(listing_id=lid, image_url=url, order=idx))
        if lid not in primary:
            l.image_url = sorted(imgs)[0][1]

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
