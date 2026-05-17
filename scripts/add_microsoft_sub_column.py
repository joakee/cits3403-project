"""Run once to add microsoft_sub column to existing User table."""
from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text(
            "ALTER TABLE user ADD COLUMN microsoft_sub VARCHAR(128)"
        ))
        db.session.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_user_microsoft_sub ON user (microsoft_sub)"
        ))
        db.session.commit()
        print("Added microsoft_sub column.")
    except Exception as e:
        print(f"Migration likely already applied or failed: {e}")
