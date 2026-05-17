from datetime import datetime

from app import db
from app.models import User, Listing, Conversation, Message
from app.routes.chat import format_awst


def test_message_has_timestamp(app):
    with app.app_context():
        seller = User(
            username="seller_test_msg",
            email="seller_msg@test.com",
            password_hash="test"
        )
        buyer = User(
            username="buyer_test_msg",
            email="buyer_msg@test.com",
            password_hash="test"
        )

        db.session.add_all([seller, buyer])
        db.session.commit()

        listing = Listing(
            title="Test Chat Listing",
            description="A listing for message testing",
            price=10.0,
            category="Books",
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
            content="Hello"
        )

        db.session.add(message)
        db.session.commit()

        assert message.timestamp is not None
        assert message.content == "Hello"


def test_format_awst_adds_awst_label():
    timestamp = datetime(2026, 5, 17, 11, 30)

    formatted = format_awst(timestamp)

    assert "AWST" in formatted
    assert "17 May 2026" in formatted