from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import BYTEA
from datetime import datetime

Base = declarative_base()

# Constants for message types
MESSAGE_TYPE_USER = "user"
MESSAGE_TYPE_BOT = "bot"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    chats = relationship("Chat", back_populates="user")


class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", order_by="Message.timestamp")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime)
    text = Column(Text, nullable=True)
    image = Column(BYTEA, nullable=True)
    message_type = Column(String, nullable=False)
