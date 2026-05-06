from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db, socketio
from app.models import User, Message, Listing, Conversation
from app.forms import EditProfileForm
from flask_socketio import emit, join_room
from datetime import datetime, timezone, timedelta
import emoji

bp = Blueprint('chat', __name__, url_prefix='/chat')

# --- ROUTES ---

@bp.route('/start/<int:listing_id>')
@login_required
def start_chat(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.is_removed and not (current_user.is_admin or current_user.is_moderator):
        abort(404)
    if listing.seller_id == current_user.id:
        return "You cannot buy your own item!", 400

    # Check if conversation already exists
    conversation = Conversation.query.filter_by(
        listing_id=listing_id, 
        buyer_id=current_user.id
    ).first()

    if not conversation:
        conversation = Conversation(
            listing_id=listing_id,
            buyer_id=current_user.id,
            seller_id=listing.seller_id
        )
        db.session.add(conversation)
        db.session.commit()

    return redirect(url_for('chat.chat_room', conversation_id=conversation.id))

@bp.route('/<int:conversation_id>')
@login_required
def chat_room(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    # Security: Ensure current user is part of the chat
    if current_user.id not in [conversation.buyer_id, conversation.seller_id]:
        return "Unauthorized", 403
    
    messages = conversation.messages.order_by(Message.timestamp.asc()).all()
    return render_template('chat/chat.html', conversation=conversation, messages=messages,User=User)

@bp.route('/inbox')
@login_required
def inbox():
    # Fetch conversations where user is buyer OR seller
    conversations = Conversation.query.filter(
        (Conversation.buyer_id == current_user.id) | 
        (Conversation.seller_id == current_user.id)
    ).all()
    
    # Sort them by the timestamp of the last message (optional but recommended)
    conversations.sort(key=lambda x: x.messages.order_by(Message.timestamp.desc()).first().timestamp if x.messages.first() else x.created_at, reverse=True)
    
    return render_template('chat/inbox.html', conversations=conversations,Message=Message,User=User)

# --- SOCKET.IO EVENTS ---

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    msg_content = data['message']

    text = emoji.emojize(msg_content)

    new_msg = Message(
        conversation_id=room,
        sender_id=current_user.id,
        content=text
    )
    db.session.add(new_msg)
    db.session.commit()

    emit('receive_message', {
        'message': text,
        'sender': current_user.id,
        'timestamp': datetime.now(timezone.utc).strftime('%H:%M')
    }, room=room)

    emit('update_inbox', {
        'conversation_id': room,
        'message': text,
        'timestamp': datetime.now(timezone.utc).strftime('%H:%M')
    }, broadcast=True)