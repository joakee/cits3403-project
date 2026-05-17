from app import db
from app.models import User, Listing, Conversation, Message
from werkzeug.security import generate_password_hash


def test_chat_page_shows_message_timestamp(client, app):
    with app.app_context():
        seller = User(
            username="seller_chat",
            email="seller_chat@test.com",
            password_hash=generate_password_hash("password123"),
            is_verified=True
        )

        buyer = User(
            username="buyer_chat",
            email="buyer_chat@test.com",
            password_hash=generate_password_hash("password123"),
            is_verified=True
        )

        db.session.add_all([seller, buyer])
        db.session.commit()

        listing = Listing(
            title="Chat Test Item",
            description="Testing chat timestamp",
            price=15.0,
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
            content="Hello timestamp"
        )

        db.session.add(message)
        db.session.commit()

        conversation_id = conversation.id
        buyer_id = buyer.id

    # Log in the buyer directly for the test
    with client.session_transaction() as session:
        session["_user_id"] = str(buyer_id)
        session["_fresh"] = True

    response = client.get(f"/chat/{conversation_id}")

    assert response.status_code == 200
    assert b"Hello timestamp" in response.data
    assert b"AWST" in response.data