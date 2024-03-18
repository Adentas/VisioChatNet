import os
from flask import Flask
from flask_mail import Mail
from src.conf.config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.getenv("SECRET_KEY")

mail = Mail(app)

