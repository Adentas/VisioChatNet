# history_routes.py
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from src.database.db import (
    get_db,
)  # Update the import path according to your project structure
from src.database.repository import (
    create_user,
    start_chat,
    send_message,
    get_user_chats,
    get_chat_history,
)

history_bp = Blueprint("history_bp", __name__)


@history_bp.route("/create_user", methods=["POST"])
def api_create_user():
    user_id = request.json["user_id"]
    db: Session = next(get_db())
    user = create_user(db, user_id=user_id)
    return (
        jsonify({"user_id": user.id})
        if user
        else jsonify({"error": "Failed to create user"})
    ), 400


@history_bp.route("/start_chat", methods=["POST"])
def api_start_chat():
    user_id = request.json["user_id"]
    db: Session = next(get_db())
    chat = start_chat(db, user_id=user_id)
    return (
        jsonify({"chat_id": chat.id})
        if chat
        else jsonify({"error": "Failed to start chat"})
    ), 400


@history_bp.route("/send_message", methods=["POST"])
def api_send_message():
    # Extract needed information from request
    chat_id = request.json["chat_id"]
    user_id = request.json["user_id"]
    message_type = request.json["message_type"]
    text = request.json.get("text", None)
    image = request.files.get("image", None)  # Assuming image is sent as a file
    db: Session = next(get_db())
    message = send_message(
        db,
        chat_id=chat_id,
        user_id=user_id,
        message_type=message_type,
        text=text,
        image=image.read() if image else None,
    )
    return (
        jsonify({"message_id": message.id})
        if message
        else jsonify({"error": "Failed to send message"})
    ), 400


@history_bp.route("/get_user_chats", methods=["GET"])
def api_get_user_chats():
    user_id = request.args.get("user_id")  # Assume user_id is passed as query parameter
    db: Session = next(get_db())
    chats = get_user_chats(db, user_id=int(user_id))
    return (
        jsonify(chats) if chats else jsonify({"error": "Failed to retrieve chats"})
    ), 400


@history_bp.route("/get_chat_history", methods=["GET"])
def api_get_chat_history():
    chat_id = request.args.get("chat_id")  # Assume chat_id is passed as query parameter
    db: Session = next(get_db())
    messages = get_chat_history(db, chat_id=int(chat_id))
    if messages is not None:
        messages_formatted = [
            {
                "id": message.id,
                "chat_id": message.chat_id,
                "user_id": message.user_id,
                "timestamp": message.timestamp.isoformat(),
                "text": message.text,
                "message_type": message.message_type,
                # Assuming you handle image as a binary. You may need to convert this to a URL or similar for display.
            }
            for message in messages
        ]
        return jsonify(messages_formatted)
    else:
        return jsonify({"error": "Failed to retrieve chat history"}), 400
