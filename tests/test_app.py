import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
from io import BytesIO
from src.app import preprocess_image
from src.app import app

class TestPreprocessImage(unittest.TestCase):
    def test_image_preprocessing(self):
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        processed_img = preprocess_image(img_bytes)

        self.assertEqual(processed_img.shape, (1, 32, 32, 3))
        self.assertTrue(processed_img.min() >= 0.0 and processed_img.max() <= 1.0)

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)

    def test_healthchecker_route(self):
        response = self.client.get('/healthchecker')
        self.assertEqual(response.status_code, 200)

    @patch('app.model.predict') 
    def test_upload_predict(self, mock_predict):
        mock_predict.return_value = [[0.1, 0.9]]
        with open('tests/images/cat.jpg', 'rb') as img:
            data = {
                'file': (img, 'cat.jpg')
            }
            response = self.client.post('/upload_predict', content_type='multipart/form-data', data=data)

            self.assertEqual(response.status_code, 200)
            self.assertIn('I think it\'s a', response.get_json()['result'])


if __name__ == '__main__':
    unittest.main()
