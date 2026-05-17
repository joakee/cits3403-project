"""
Selenium end-to-end tests for the UWA Marketplace.

Prerequisites:
  - The live server must be running: `python run.py`
  - Chrome or Edge must be installed

Run:
  pytest tests/test_selenium.py -v

Run with a visible browser window (for debugging):
  SELENIUM_HEADLESS=0 pytest tests/test_selenium.py -v

Run against a different server URL:
  TEST_SERVER_URL=http://localhost:5001 pytest tests/test_selenium.py -v
"""
import os
import sys
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User, Listing, ListingView
from config import Config

_CHROME_PATHS_WIN = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
]


def _find_chrome_binary():
    if sys.platform != "win32":
        return None
    for path in _CHROME_PATHS_WIN:
        if os.path.isfile(path):
            return path
    return None


def _make_driver(headless: bool):
    """Try Chrome first, then Edge using Selenium Manager. Returns a WebDriver or skips."""
    common_args = ["--no-sandbox", "--disable-dev-shm-usage", "--window-size=1920,1080"]

    # --- Chrome ---
    chrome_bin = _find_chrome_binary()
    if chrome_bin or sys.platform != "win32":
        try:
            opts = ChromeOptions()
            if chrome_bin:
                opts.binary_location = chrome_bin
            if headless:
                opts.add_argument("--headless=new")
            for arg in common_args:
                opts.add_argument(arg)
            return webdriver.Chrome(options=opts)
        except Exception:
            pass

    # --- Edge (pre-installed on Windows 11, managed by Selenium Manager) ---
    try:
        opts = EdgeOptions()
        if headless:
            opts.add_argument("--headless=new")
        for arg in common_args:
            opts.add_argument(arg)
        return webdriver.Edge(options=opts)
    except Exception:
        pass

    pytest.skip("No supported browser found (Chrome or Edge). Install one to run Selenium tests.")

BASE_URL = os.environ.get('TEST_SERVER_URL', 'http://localhost:5001')

_TEST_EMAIL = 'selenium_test@uwa.example'
_TEST_PASSWORD = 'SeleniumPass123'
_TEST_USERNAME = 'SeleniumTestUser'


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def test_db_user():
    """Insert a verified test user directly into the live marketplace.db."""
    app = create_app(Config)
    with app.app_context():
        existing = User.query.filter_by(email=_TEST_EMAIL).first()
        if existing:
            for lst in Listing.query.filter_by(seller_id=existing.id).all():
                ListingView.query.filter_by(listing_id=lst.id).delete()
                db.session.delete(lst)
            db.session.delete(existing)
            db.session.commit()

        user = User(
            username=_TEST_USERNAME,
            email=_TEST_EMAIL,
            password_hash=generate_password_hash(_TEST_PASSWORD),
            is_verified=True,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    yield user_id

    with app.app_context():
        user = db.session.get(User, user_id)
        if user:
            for lst in Listing.query.filter_by(seller_id=user_id).all():
                ListingView.query.filter_by(listing_id=lst.id).delete()
                db.session.delete(lst)
            db.session.delete(user)
            db.session.commit()


@pytest.fixture(scope='module')
def test_db_listing(test_db_user):
    """Insert a known listing (title starts with 'Selenium Test') into the live DB."""
    app = create_app(Config)
    with app.app_context():
        listing = Listing(
            title='Selenium Test Textbook',
            description='Automated test listing — safe to ignore.',
            price=42.00,
            category='books',
            seller_id=test_db_user,
        )
        db.session.add(listing)
        db.session.commit()
        listing_id = listing.id

    yield listing_id

    with app.app_context():
        ListingView.query.filter_by(listing_id=listing_id).delete()
        lst = db.session.get(Listing, listing_id)
        if lst:
            db.session.delete(lst)
        db.session.commit()


@pytest.fixture(scope='module')
def driver():
    """Shared browser instance for all selenium tests in this module (Chrome or Edge)."""
    headless = os.environ.get('SELENIUM_HEADLESS', '1') != '0'
    drv = _make_driver(headless)
    drv.implicitly_wait(10)
    yield drv
    drv.quit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _login(driver):
    """Navigate to the login page, fill in test credentials, and wait for redirect."""
    driver.get(f'{BASE_URL}/auth/login')
    driver.find_element(By.ID, 'login-email').clear()
    driver.find_element(By.ID, 'login-email').send_keys(_TEST_EMAIL)
    driver.find_element(By.ID, 'login-password').clear()
    driver.find_element(By.ID, 'login-password').send_keys(_TEST_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
    WebDriverWait(driver, 10).until(EC.url_contains('/listings'))


def _logout(driver):
    """Navigate to the logout endpoint and wait for the login-page redirect."""
    driver.get(f'{BASE_URL}/auth/logout')
    WebDriverWait(driver, 10).until(EC.url_contains('/auth/login'))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_home_page_loads(driver, test_db_user):
    """Home page renders with the correct title and a visible navbar brand."""
    driver.get(BASE_URL)
    assert 'UWA Marketplace' in driver.title
    brand = driver.find_element(By.CSS_SELECTOR, '.navbar-brand')
    assert 'UWA Marketplace' in brand.text
    assert '500' not in driver.title


def test_login_success(driver, test_db_user):
    """Valid credentials redirect the user to the listings browse page."""
    _logout(driver)
    driver.get(f'{BASE_URL}/auth/login')
    driver.find_element(By.ID, 'login-email').send_keys(_TEST_EMAIL)
    driver.find_element(By.ID, 'login-password').send_keys(_TEST_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
    WebDriverWait(driver, 10).until(EC.url_contains('/listings'))
    assert '/listings' in driver.current_url
    _logout(driver)


def test_login_invalid_credentials(driver, test_db_user):
    """Wrong password keeps the user on the login page and shows a flash error."""
    _logout(driver)
    driver.get(f'{BASE_URL}/auth/login')
    driver.find_element(By.ID, 'login-email').send_keys(_TEST_EMAIL)
    driver.find_element(By.ID, 'login-password').send_keys('totally-wrong-password')
    driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
    WebDriverWait(driver, 10).until(EC.url_contains('/auth/login'))
    assert '/auth/login' in driver.current_url
    alert = driver.find_element(By.CSS_SELECTOR, '.alert')
    assert alert.is_displayed()


def test_unauthenticated_redirect_to_login(driver):
    """Accessing a login-required route while logged out redirects to the login page."""
    _logout(driver)
    driver.get(f'{BASE_URL}/listings/new')
    WebDriverWait(driver, 10).until(EC.url_contains('/auth/login'))
    assert '/auth/login' in driver.current_url


def test_browse_listings_page(driver, test_db_listing):
    """Listings browse page shows at least one listing card, each with a dollar-sign price."""
    driver.get(f'{BASE_URL}/listings')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'listings-grid'))
    )
    cards = driver.find_elements(By.CSS_SELECTOR, '.listing-card')
    assert len(cards) > 0
    prices = driver.find_elements(By.CSS_SELECTOR, '.listing-price')
    assert len(prices) > 0
    assert all('$' in p.text for p in prices)


def test_search_by_keyword(driver, test_db_listing):
    """Typing a keyword in the search bar filters results and appends q= to the URL."""
    driver.get(f'{BASE_URL}/listings')
    search = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'listings-search'))
    )
    search.clear()
    search.send_keys('Selenium Test')
    driver.find_element(By.CSS_SELECTOR, '.listings-filter-bar button[type="submit"]').click()
    WebDriverWait(driver, 10).until(EC.url_contains('q='))
    assert 'q=' in driver.current_url
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.listing-card'))
    )
    titles = [el.text for el in driver.find_elements(By.CSS_SELECTOR, '.listing-card .card-title')]
    assert any('Selenium Test' in t for t in titles)


def test_category_filter(driver, test_db_listing):
    """Selecting 'books' from the category dropdown appends category=books to the URL."""
    driver.get(f'{BASE_URL}/listings')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="category"]'))
    )
    Select(driver.find_element(By.CSS_SELECTOR, 'select[name="category"]')).select_by_value('books')
    driver.find_element(By.CSS_SELECTOR, '.listings-filter-bar button[type="submit"]').click()
    WebDriverWait(driver, 10).until(EC.url_contains('category=books'))
    assert 'category=books' in driver.current_url
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'listings-grid'))
    )
    # At minimum our test listing (category=books) should be present
    cards = driver.find_elements(By.CSS_SELECTOR, '.listing-card')
    assert len(cards) > 0


def test_listing_detail_page(driver, test_db_listing):
    """Clicking a listing card title opens its detail page with price and detail wrapper."""
    driver.get(f'{BASE_URL}/listings')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.listing-card .card-title a'))
    )
    # Navigate via href to avoid stretched-link interception
    link = driver.find_element(By.CSS_SELECTOR, '.listing-card .card-title a')
    href = link.get_attribute('href')
    driver.get(href)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'listing-detail'))
    )
    assert driver.find_element(By.ID, 'listing-detail').is_displayed()
    price_el = driver.find_element(By.CSS_SELECTOR, '.listing-price')
    assert '$' in price_el.text
    assert 'Browse Listings' not in driver.title


def test_create_new_listing(driver, test_db_user):
    """A logged-in user can fill the new-listing form and see their listing on the detail page."""
    _login(driver)
    driver.get(f'{BASE_URL}/listings/new')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="title"]'))
    )
    driver.find_element(By.CSS_SELECTOR, 'input[name="title"]').send_keys('My Selenium Created Listing')
    driver.find_element(By.CSS_SELECTOR, 'textarea[name="description"]').send_keys(
        'Created by automated Selenium test — safe to delete.'
    )
    driver.find_element(By.CSS_SELECTOR, 'input[name="price"]').send_keys('19.99')
    Select(driver.find_element(By.CSS_SELECTOR, 'select[name="category"]')).select_by_value('other')
    driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
    # On success, the route redirects to the newly created listing's detail page
    WebDriverWait(driver, 10).until(
        lambda d: '/listings/new' not in d.current_url and '/listings/' in d.current_url
    )
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'listing-detail'))
    )
    assert 'My Selenium Created Listing' in driver.page_source
    _logout(driver)


def test_logout_flow(driver, test_db_user):
    """After clicking Logout the session ends and protected routes redirect to login."""
    _login(driver)
    logout_link = driver.find_element(By.PARTIAL_LINK_TEXT, 'Logout')
    assert logout_link.is_displayed()
    logout_link.click()
    WebDriverWait(driver, 10).until(EC.url_contains('/auth/login'))
    assert '/auth/login' in driver.current_url
    # The navbar should now show a "Log In" link instead of "Logout"
    login_nav = driver.find_element(By.PARTIAL_LINK_TEXT, 'Log In')
    assert login_nav.is_displayed()
    # Attempting a protected route should still redirect to login
    driver.get(f'{BASE_URL}/listings/new')
    WebDriverWait(driver, 10).until(EC.url_contains('/auth/login'))
    assert '/auth/login' in driver.current_url
