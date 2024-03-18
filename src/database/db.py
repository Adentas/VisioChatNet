from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.conf.config import settings

# Database URL from environment variable
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

# Ensure the environment variable is set
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("No DATABASE_URL set for Flask application")

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=90,  # Adjust pool size here
    max_overflow=110)  # Adjust max overflow here)

# Create a SessionLocal class which will serve as a factory for new Session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
