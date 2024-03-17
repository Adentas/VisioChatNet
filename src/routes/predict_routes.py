from src.database.db import get_db
from src.repository.chat_repository import start_chat
from src.repository.predict_repository import get_predictions
from src.routes.history_routes import api_start_chat

from flask import Blueprint, request, jsonify, render_template
from flask_login import current_user

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/upload_predict', methods=['POST', 'GET'])
def upload_predict():
    if current_user.is_authenticated:
        api_start_chat()

    return render_template("chat/chat.html")

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@predict_bp.route('/get_predictions', methods=['POST'])
def api_get_predictions():
    uploaded_file = request.files.get("file")
    if uploaded_file and allowed_file(uploaded_file.filename):
        return jsonify({"result": get_predictions(uploaded_file)})
    else:
        return jsonify({"error": "Oops, I'm not quite sure how to handle this image format. Could you please try sending a photo in jpg or jpeg format?"}), 400