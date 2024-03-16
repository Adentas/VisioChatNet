from src.database.db import get_db
from src.repository.chat_repository import start_chat
from src.repository.predict_repository import get_predictions

from flask import Blueprint, request, jsonify, render_template
from flask_login import current_user

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/upload_predict', methods=['POST', 'GET'])
def upload_predict():
    if current_user.is_authenticated:
        # Start or retrieve a chat session for authenticated users
        db = get_db()  # Ensure this gets an active session
        chat = start_chat(db, user_id=current_user.id)
        global chat_id
        chat_id = chat.id

    if request.method == "POST":
        uploaded_file = request.files.get("file")
        return jsonify({"result": get_predictions(uploaded_file)})

    return render_template("chat/chat.html")