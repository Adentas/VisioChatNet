import numpy as np

from src.model_loader import get_model
from src.repository.chat_repository import send_message
from src.database.db import get_db
from src.utils.preproccss_image import preprocess_image
from flask import session

from flask import Blueprint, request, jsonify, render_template
from flask_login import current_user

def get_predictions(image):
    model = get_model()
    if image is not None:
        print("Trying to write image in databes")
        if current_user.is_authenticated:
            print("User is authorized")
            db = get_db()
            send_message(
                db, session["current_chat_id"], current_user.id, "user", image=image
            )
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

        # Write the bot's response to the database
        if current_user.is_authenticated and session["current_chat_id"]:
            db = get_db()
            send_message(
                db=db,
                chat_id=session["current_chat_id"],
                user_id=current_user.id,  # Use bot's user ID if it's different
                message_type="bot",
                text=response_message,
            )

        return response_message
    