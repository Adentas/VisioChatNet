import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv(".env", encoding="utf-8")


class Config:
    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@"
        f"{os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}/"
        f"{os.environ.get('POSTGRES_DB')}?sslmode=require"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    postgres_user = os.environ.get("POSTGRES_USER")
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    postgres_host = os.environ.get("POSTGRES_HOST")
    postgres_port = os.environ.get("POSTGRES_PORT")
    postgres_db = os.environ.get("POSTGRES_DB")
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEBUG = False


settings = Config()
