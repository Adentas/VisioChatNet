import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.models import Chat, Message  # Assuming models.py contains our ORM models
from werkzeug.datastructures import FileStorage
from src.utils.cache_config import cache, generate_chat_history_cache_key, generate_user_chat_cache_key
from flask_login import current_user


def start_chat(db: Session, user_id: int):
    try:
        new_chat = Chat(user_id=user_id, title="Classified image")
        db.add(new_chat)
        db.flush()  # This ensures 'new_chat.id' is available without committing the transaction

        # Add a welcome message to the chat
        welcome_message = Message(
            chat_id=new_chat.id,
            user_id=user_id,  # Replace with the actual bot's user ID
            message_type="bot",
            text="Hi, welcome to VisioNet! Go ahead and send me your image, and I’ll tell you who’s in it. 😊",
        )
        db.add(welcome_message)

        db.commit()  # Commit both the chat and message together as a single transaction
        cache.delete(f"user_chats_{user_id}")
        return new_chat
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Can't start chat for user_id {user_id}: {str(e)}")
        return None


def send_message(
    db: Session,
    chat_id: int,
    user_id: int,
    message_type: str,
    text: str = None,
    image: FileStorage = None,
):
    image_binary = image.read() if image else None
    try:
        new_message = Message(
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            image=image_binary,  # Use the binary data
            timestamp=datetime.now().isoformat(),
            message_type=message_type,
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        cache.delete(f"chat_history_{chat_id}")
        cache.delete(f"user_chats_{user_id}")

        return new_message
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Can't send message in chat_id {chat_id}: {str(e)}")
        return None

def get_user_chats(db: Session, user_id: int):
    cache_key = f"user_chats_{user_id}"
    cached_chats = cache.get(cache_key)
    if cached_chats is not None:
        return cached_chats
    try:
        chats = db.query(Chat).filter(Chat.user_id == user_id).all()
        chat_data = [{"id": chat.id, "title": chat.title} for chat in chats]
        cache.set(cache_key, chat_data, timeout=300)
        return chat_data
    except SQLAlchemyError as e:
        logging.error(f"Can't retrieve chats for user_id {user_id}: {str(e)}")
        return None

def get_chat_history(db: Session, chat_id: int):
    cache_key = f"chat_history_{chat_id}"
    cached_messages = cache.get(cache_key)
    if cached_messages is not None:
        return cached_messages
    try:
        messages = (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.timestamp)
            .all()
        )
        cache.set(cache_key, messages, timeout=300)
        return messages
    except SQLAlchemyError as e:
        logging.error(f"Can't retrieve chat history for chat_id {chat_id}: {str(e)}")
        return None


def delete_chat(db: Session, chat_id: int) -> bool:
    """
    Deletes a chat and all associated messages from the database.

    Parameters:
    - db: The database session.
    - chat_id: The ID of the chat to be deleted.

    Returns:
    - True if the chat was successfully deleted, False otherwise.
    """
    try:
        chat  = db.query(Chat).filter(Chat.id == chat_id).one_or_none()
        if chat:
            db.delete(chat)
            db.commit()
            cache.delete(f"chat_history_{chat_id}")
            return True
    except SQLAlchemyError as e:
        logging.error(f"Can't delete chat with chat_id {chat_id}: {str(e)}")
        db.rollback()
        return False


def rename_chat(db: Session, chat_id: int, new_title: str) -> bool:
    try:
        chat = db.query(Chat).filter(Chat.id == chat_id).one_or_none()
        if chat:
            chat.title = new_title
            db.commit()
            return True
        return False
    except SQLAlchemyError as e:
        logging.error(f"Can't rename chat with chat_id {chat_id}: {str(e)}")
        db.rollback()
        return False
