from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.models import Base
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Use SQLite for simplicity
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()