import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv(".env", encoding="utf-8")

class Config:
    SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ...

app = Flask(__name__)
app.config.from_object(Config)