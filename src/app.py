import os

from sqlalchemy import text
from src.database.db import SessionLocal,get_db
from src.database.repository import start_chat,send_message
from src.auth_routes import auth_bp
from src.database.models import User

from flask import Flask, request, jsonify, render_template
from flask_login import LoginManager, current_user
from src.routes.history_routes import history_bp
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(history_bp)

# model = load_model('src/ai/CIFAR_10.hdf5')


@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    return db.query(User).get(int(user_id))


model = load_model('../src/ai/CIFAR_10.hdf5')
chat_id = -1


def preprocess_image(uploaded_file):
    img = Image.open(uploaded_file)
    img = img.resize((32, 32))
    img_array = np.array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


@app.route("/")
def home():
    return render_template("home/home.html")


def get_predictions(image):
    if image is not None:
        if current_user.is_authenticated:
            send_message(get_db(), chat_id, current_user.id, "user", image=image)
        # Processing the image and getting predictions from the model
        processed_image = preprocess_image(image)
        prediction = model.predict(processed_image)[0]

        # Obtaining indices and probabilities of the top 3 classes
        top3_indices = np.argsort(prediction)[-3:][::-1]
        top3_probabilities = prediction[top3_indices]

        # Classes names
        classes = [
            "airplane",
            "automobile",
            "bird",
            "cat",
            "deer",
            "dog",
            "frog",
            "horse",
            "ship",
            "truck",
        ]

        # Adding the most likely class with its probability
        most_likely_class_index = top3_indices[0]
        most_likely_class_probability = top3_probabilities[0] * 100
        response_message = f"I think it's a - {classes[most_likely_class_index]} with a probability {most_likely_class_probability:.2f}%.\n\n"

        # Additionally, we display other classes and their probabilities
        response_message += "Also, I have other options:\n"
        for i, index in enumerate(top3_indices[1:], start=1):
            class_probability = top3_probabilities[i] * 100
            response_message += (
                f"{i}: {classes[index]} with a probability {class_probability:.2f}%\n"
            )

        return response_message


@app.route("/upload_predict", methods=["POST", "GET"])
def upload_predict():
    if current_user.is_authenticated:
        # Start or retrieve a chat session for authenticated users
        chat = start_chat(get_db, user_id=current_user.id)
        global chat_id 
        chat_id = chat.id

    if request.method == "POST":
        uploaded_file = request.files.get("file")
        return jsonify({"result": get_predictions(uploaded_file)})

    return render_template("base.html")


@app.route("/api/is_authenticated")
def is_authenticated():
    return jsonify({"authenticated": current_user.is_authenticated})


@app.route("/healthchecker")
def healthchecker():
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()
        if result is None:
            return jsonify({"detail": "Database is not configured correctly"}), 500
        return jsonify({"message": "Welcome to Flask! Database connected correctly"})
    except Exception as e:
        return jsonify({"detail": f"Error connecting to the database: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
