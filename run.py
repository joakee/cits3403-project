#!/usr/bin/env python3

from app import create_app, db, socketio

app = create_app()


def _migrate_columns():
    """Add new columns to existing tables without dropping data."""
    from sqlalchemy import text, inspect
    inspector = inspect(db.engine)

    user_cols = {c['name'] for c in inspector.get_columns('user')}
    listing_cols = {c['name'] for c in inspector.get_columns('listing')}

    new_user_cols = {
        'is_store':       'BOOLEAN DEFAULT 0',
        'is_verified':    'BOOLEAN DEFAULT 0',
        'is_admin':       'BOOLEAN DEFAULT 0',
        'store_name':     'VARCHAR(128)',
        'store_address':  'VARCHAR(256)',
        'contact_phone':  'VARCHAR(32)',
        'contact_email':  'VARCHAR(120)',
        'store_bio':      'TEXT',
        'banned_at':      'DATETIME',
        'ban_reason':     'TEXT',
    }
    new_listing_cols = {
        'stock_quantity':  'INTEGER',
        'posted_as_store': 'BOOLEAN DEFAULT 0',
        'is_removed':      'BOOLEAN DEFAULT 0',
        'removed_at':      'DATETIME',
        'removed_reason':  'TEXT',
        'removed_by_id':   'INTEGER',
    }

    message_cols = {c['name'] for c in inspector.get_columns('message')}
    new_message_cols = {
        'is_read': 'BOOLEAN DEFAULT 0',
    }

    with db.engine.connect() as conn:
        for col, typedef in new_user_cols.items():
            if col not in user_cols:
                conn.execute(text(f'ALTER TABLE "user" ADD COLUMN {col} {typedef}'))
        for col, typedef in new_listing_cols.items():
            if col not in listing_cols:
                conn.execute(text(f'ALTER TABLE listing ADD COLUMN {col} {typedef}'))
        for col, typedef in new_message_cols.items():
            if col not in message_cols:
                conn.execute(text(f'ALTER TABLE message ADD COLUMN {col} {typedef}'))
        conn.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        _migrate_columns()
    socketio.run(app, debug=True, port=5001, host='0.0.0.0', allow_unsafe_werkzeug=True)
