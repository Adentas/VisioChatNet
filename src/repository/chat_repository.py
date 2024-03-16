import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..database.db import get_db  # Assuming db.py contains the get_db function
from ..models.models import User, Chat, Message  # Assuming models.py contains our ORM models
from werkzeug.datastructures import FileStorage


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
        print("Sending message")
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
        print("Message succesfully sent")
        return new_message
    except SQLAlchemyError as e:
        db.rollback()
        print("Message was not sent")
        logging.error(f"Can't send message in chat_id {chat_id}: {str(e)}")
        return None


def get_user_chats(db: Session, user_id: int):
    try:
        chats = db.query(Chat).filter(Chat.user_id == user_id).all()
        return [{"id": chat.id, "title": chat.title} for chat in chats]
    except SQLAlchemyError as e:
        logging.error(f"Can't retrieve chats for user_id {user_id}: {str(e)}")
        return None


def get_chat_history(db: Session, chat_id: int):
    try:
        messages = (
            db.query(Message)
            .filter(Message.chat_id == chat_id)
            .order_by(Message.timestamp)
            .all()
        )
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
            return True
    except SQLAlchemyError as e:
        logging.error(f"Can't delete chat with chat_id {chat_id}: {str(e)}")
        db.rollback()
        return False