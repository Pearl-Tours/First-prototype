from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime, timedelta

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(200))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Tour(Base):
    __tablename__ = "tours"
    id = Column(Integer, primary_key=True, index=True)
    Title= Column(String(100), index=True)
    description = Column(String(500))
    price = Column(Float)
    duration= Column(String(50))
    locations = Column(String(100))
    image_url = Column(String(200))
    created_at= Column(DateTime,default=datetime.utcnow)
    updated_at= Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    is_active= Column(Boolean, default=True)
    images= relationship("TourImage", backref="tour",cascade="all, delete-orphan")
    
class TourImage(Base):
    __tablename__ = "tour_images"
    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"))
    image_url = Column(String(200))
    is_primary = Column(Boolean, default=False)