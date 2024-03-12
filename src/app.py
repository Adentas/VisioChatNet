from flask import Flask, request, jsonify, render_template
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)

model = load_model('./ai/CIFAR_10.hdf5')

def preprocess_image(uploaded_file):
    img = Image.open(uploaded_file)
    img = img.resize((32, 32))
    img_array = np.array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


@app.route('/upload_predict', methods=['POST', 'GET'])
def upload_predict():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file is not None:
            # Обробка зображення та отримання передбачень від моделі
            processed_image = preprocess_image(uploaded_file)
            prediction = model.predict(processed_image)[0]

            # Отримання індексів та ймовірностей топ-3 класів
            top3_indices = np.argsort(prediction)[-3:][::-1]
            top3_probabilities = prediction[top3_indices]

            # Назви класів
            classes = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

            # Додаємо найбільш вірогідний клас з його ймовірністю
            most_likely_class_index = top3_indices[0]
            most_likely_class_probability = top3_probabilities[0] * 100
            response_message = f"I think it's a - {classes[most_likely_class_index]} with a probability {most_likely_class_probability:.2f}%.\n\n"

            # Додатково виводимо інші класи та їх ймовірності
            response_message += "Also, I have other options:\n"
            for i, index in enumerate(top3_indices[1:], start=1):  # Пропускаємо найбільш вірогідний клас
                class_probability = top3_probabilities[i] * 100
                response_message += f"{i}: {classes[index]} with a probability {class_probability:.2f}%\n"

            return jsonify({'result': response_message})
        
    return render_template('base.html')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5002)