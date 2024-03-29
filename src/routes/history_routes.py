# history_routes.py
import base64
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from werkzeug.exceptions import BadRequest
from sqlalchemy.orm import Session
from flask_login import current_user
from src.database.db import (
    get_db,
)
from src.repository.chat_repository import (
    start_chat,
    delete_chat,
    send_message,
    get_user_chats,
    get_chat_history,
    rename_chat
)

history_bp = Blueprint("history_bp", __name__)


@history_bp.route("/start_chat", methods=["POST"])
def api_start_chat():
    user_id = current_user.id
    db = get_db()
    chat = start_chat(db, user_id=user_id)
    if chat:
        session["current_chat_id"] = chat.id  # Store chat_id in the session
        session.modified = True
        return jsonify({"chat_id": chat.id}), 200
    else:
        return jsonify({"error": "Failed to start chat"}), 400


@history_bp.route("/set_current_chat", methods=["POST"])
def set_current_chat():
    chat_id = request.json.get("chat_id")
    if chat_id:
        session["current_chat_id"] = chat_id  # Store chat_id in the session
        session.modified = True
        return jsonify({"message": "Current chat set successfully"}), 200
    else:
        return jsonify({"error": "Chat ID is required"}), 400


@history_bp.route("/get_current_chat")
def get_current_chat():
    chat_id = session["current_chat_id"]
    if chat_id:
        return jsonify({"chat_id": chat_id}), 200
    else:
        return jsonify({"error": "No active chat"}), 404


@history_bp.route("/send_message", methods=["POST"])
def api_send_message():
    try:
        chat_id = request.json["chat_id"]
        user_id = request.json["user_id"]
        message_type = request.json["message_type"]
        text = request.json.get("text", None)
        image = request.files.get("image", None)
        image_bytes = image.read() if image else None
        db: Session = get_db()
        message = send_message(
            db,
            chat_id=chat_id,
            user_id=user_id,
            message_type=message_type,
            text=text,
            image=image_bytes,
        )
        if not message:
            raise BadRequest("Failed to send message")
        return jsonify({"message_id": message.id}), 200
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Log the exception details here
        return jsonify({"error": "Internal server error"}), 500


@history_bp.route("/get_user_chats", methods=["GET"])
def api_get_user_chats():
    if current_user.is_authenticated:
        db: Session = get_db()
        chats = get_user_chats(db, user_id=current_user.id)
        return jsonify(chats if chats else {"error": "Failed to retrieve chats"}), 200
    else:
        return jsonify({"error": "User not authenticated"}), 401


@history_bp.route("/get_chat_history", methods=["GET"])
def api_get_chat_history():
    chat_id = request.args.get("chat_id")
    db: Session = get_db()
    messages = get_chat_history(db, chat_id=int(chat_id))
    if messages is not None:
        messages_formatted = [
            {
                "id": message.id,
                "chat_id": message.chat_id,
                "user_id": message.user_id,
                "timestamp": (
                    message.timestamp.isoformat()
                    if message.timestamp
                    else datetime.now().isoformat()
                ),
                "text": message.text,
                "message_type": message.message_type,
                "image": (
                    base64.b64encode(message.image).decode("utf-8")
                    if message.image is not None
                    else None
                ),
            }
            for message in messages
        ]
        return jsonify(messages_formatted), 200
    else:
        return jsonify({"error": "Failed to retrieve chat history"}), 400


@history_bp.route("/delete_chat", methods=["DELETE"])
def api_delete_chat():
    chat_id = request.args.get("chat_id")
    if chat_id is None:
        return jsonify({"error": "Chat ID must be provided"}), 400

    db: Session = get_db()
    success = delete_chat(db, chat_id=int(chat_id))

    if success:
        return jsonify({"message": "Chat deleted successfully."}), 200
    else:
        return jsonify({"error": "Failed to delete chat."}), 500


@history_bp.route("/rename_chat", methods=["POST"])
def api_rename_chat():
    try:
        print(request.json)  # This will output the incoming JSON payload to the logs.
        chat_id = request.json.get("chat_id")
        new_title = request.json.get("new_name")
        if not chat_id or not new_title:
            return jsonify({"error": "Chat ID and new title must be provided"}), 400

        db: Session = get_db()
        success = rename_chat(db, chat_id=int(chat_id), new_title=new_title)

        if success:
            return jsonify({"message": "Chat renamed successfully."}), 200
        else:
            return jsonify({"error": "Failed to rename chat."}), 400
    except Exception as e:
        # Log the exception details here
        return jsonify({"error": "Internal server error"}), 500
