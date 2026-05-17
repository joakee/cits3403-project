import socket
import threading
import time
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from werkzeug.security import generate_password_hash
from werkzeug.serving import make_server

from app import create_app, db
from app.models import User, Listing, Conversation, Message


class SeleniumTestConfig:
    SECRET_KEY = "selenium-test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///selenium_test.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False
    WTF_CSRF_ENABLED = False
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    UPLOAD_FOLDER = "/tmp/test-uploads"


def get_free_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


@pytest.fixture
def live_app():
    app = create_app(SeleniumTestConfig)

    with app.app_context():
        db.drop_all()
        db.create_all()

        seller = User(
            username="selenium_seller",
            email="selenium_seller@test.com",
            password_hash=generate_password_hash("password123"),
            is_verified=True
        )

        buyer = User(
            username="selenium_buyer",
            email="selenium_buyer@test.com",
            password_hash=generate_password_hash("password123"),
            is_verified=True
        )

        db.session.add_all([seller, buyer])
        db.session.commit()

        listing = Listing(
            title="Selenium Chat Item",
            description="Item for Selenium chat test",
            price=20.0,
            category="books",
            seller_id=seller.id
        )

        db.session.add(listing)
        db.session.commit()

        conversation = Conversation(
            listing_id=listing.id,
            buyer_id=buyer.id,
            seller_id=seller.id
        )

        db.session.add(conversation)
        db.session.commit()

        message = Message(
            conversation_id=conversation.id,
            sender_id=buyer.id,
            content="Existing Selenium message",
            timestamp=datetime.utcnow()
        )

        db.session.add(message)
        db.session.commit()

        conversation_id = conversation.id

    port = get_free_port()
    server = make_server("127.0.0.1", port, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    time.sleep(1)

    yield f"http://127.0.0.1:{port}", conversation_id

    server.shutdown()
    thread.join(timeout=2)

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,1000")

    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


def selenium_login(driver, base_url):
    driver.get(f"{base_url}/auth/login")

    email_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")

    email_input.send_keys("selenium_buyer@test.com")
    password_input.send_keys("password123")

    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
    submit_button.click()

    time.sleep(1)


def test_selenium_login_page_loads(driver, live_app):
    base_url, _ = live_app

    driver.get(f"{base_url}/auth/login")

    assert "login" in driver.page_source.lower() or "log in" in driver.page_source.lower()
    assert driver.find_element(By.NAME, "email")
    assert driver.find_element(By.NAME, "password")


def test_selenium_chat_timestamp_visible(driver, live_app):
    base_url, conversation_id = live_app

    selenium_login(driver, base_url)

    driver.get(f"{base_url}/chat/{conversation_id}")

    time.sleep(1)

    assert "Existing Selenium message" in driver.page_source
    assert "AWST" in driver.page_source