import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .db import get_db  # Assuming db.py contains the get_db function
from .models import User, Chat, Message  # Assuming models.py contains our ORM models


def start_chat(db: Session, user_id: int):
    try:
        new_chat = Chat(user_id=user_id)
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)
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
    image: bytes = None,
):
    try:
        new_message = Message(
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            image=image,
            message_type=message_type
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return new_message
    except SQLAlchemyError as e:
        db.rollback()
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
        # First, delete all messages associated with the chat
        db.query(Message).filter(Message.chat_id == chat_id).delete()

        # Optional: If there's a Chat model that needs to be deleted as well
        # db.query(Chat).filter(Chat.id == chat_id).delete()

        # Commit the transaction to make sure all deletions are saved
        db.commit()
        return True
    except SQLAlchemyError as e:
        logging.error(f"Can't delete chat with chat_id {chat_id}: {str(e)}")
        # Rollback in case of error to avoid leaving the DB in an inconsistent state
        db.rollback()
        return False
