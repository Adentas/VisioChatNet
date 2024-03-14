import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv(".env", encoding="utf-8")


class Config:
    SQLALCHEMY_DATABASE_URI: str = (
        "postgresql+psycopg2://user:password@localhost:5432/postgres"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    postgres_user = os.environ.get("POSTGRES_USER")
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    postgres_host = os.environ.get("POSTGRES_HOST")
    postgres_port = os.environ.get("POSTGRES_PORT")
    postgres_db = os.environ.get("POSTGRES_DB")


settings = Config()
