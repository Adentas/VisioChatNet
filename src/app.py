import os

from sqlalchemy import text
from src.database.db import SessionLocal
from src.auth_routes import auth_bp
from src.database.models import User

from flask import Flask, request, jsonify, render_template
from flask_login import LoginManager
from src.routes.history_routes import history_bp
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
app.register_blueprint(auth_bp, url_prefix='/auth')

#model = load_model('src/ai/CIFAR_10.hdf5')

@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    return db.query(User).get(int(user_id))

model = load_model('../src/ai/CIFAR_10.hdf5')

def preprocess_image(uploaded_file):
    img = Image.open(uploaded_file)
    img = img.resize((32, 32))
    img_array = np.array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

@app.route('/')
def home():
    return render_template("home/home.html")

@app.route('/upload_predict', methods=['POST', 'GET'])
def upload_predict():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file is not None:
            # Processing the image and getting predictions from the model
            processed_image = preprocess_image(uploaded_file)
            prediction = model.predict(processed_image)[0]

            # Obtaining indices and probabilities of the top 3 classes
            top3_indices = np.argsort(prediction)[-3:][::-1]
            top3_probabilities = prediction[top3_indices]

            # Classes names
            classes = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

            # Adding the most likely class with its probability
            most_likely_class_index = top3_indices[0]
            most_likely_class_probability = top3_probabilities[0] * 100
            response_message = f"I think it's a - {classes[most_likely_class_index]} with a probability {most_likely_class_probability:.2f}%.\n\n"

            # Additionally, we display other classes and their probabilities
            response_message += "Also, I have other options:\n"
            for i, index in enumerate(top3_indices[1:], start=1):
                class_probability = top3_probabilities[i] * 100
                response_message += f"{i}: {classes[index]} with a probability {class_probability:.2f}%\n"

            return jsonify({'result': response_message})

    return render_template('base.html')


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


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
    app.register_blueprint(history_bp)
