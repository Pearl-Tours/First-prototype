import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.models import Base
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://admin:1237tyu@db:3306/tourdb"
#SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Use SQLite for simplicity
engine = create_engine(SQLALCHEMY_DATABASE_URL )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()