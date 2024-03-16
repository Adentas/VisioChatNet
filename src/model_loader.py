from tensorflow.keras.models import load_model

def get_model():
    model_path = "../src/ai/CIFAR_10.hdf5"
    model = load_model(model_path)
    return model
