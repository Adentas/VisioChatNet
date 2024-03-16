from PIL import Image
import numpy as np

def preprocess_image(uploaded_file):
    img = Image.open(uploaded_file)
    img = img.resize((32, 32))
    img_array = np.array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array