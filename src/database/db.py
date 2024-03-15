from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.conf.config import settings

# Database URL from environment variable
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

# Ensure the environment variable is set
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("No DATABASE_URL set for Flask application")

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,  # This is the number of connections to keep open inside the connection pool
    max_overflow=5,  # This is the number of connections to allow "overflow" beyond the pool size
    pool_timeout=30,  # Specifies the number of seconds to wait before giving up on returning a connection from the pool
    pool_recycle=1800,  # forces the pool to recycle connections after the given number of seconds has passed
)

# Create a SessionLocal class which will serve as a factory for new Session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
