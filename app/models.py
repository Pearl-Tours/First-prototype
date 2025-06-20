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
    newsletter_subscribed = Column(Boolean, default=False)
    unsubscribe_token=Column(String(36), default=lambda:str(uuid.uuid4()))

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Tour(Base):
    __tablename__ = "tours"
    id = Column(Integer, primary_key=True, index=True)
    title= Column(String(100), index=True)
    description = Column(String(500))
    price = Column(Float)
    duration= Column(String(50))
    locations = Column(String(100))
    image_url = Column(String(200))
    created_at= Column(DateTime,default=datetime.utcnow)
    updated_at= Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    is_active= Column(Boolean, default=True)
    images= relationship("TourImage", backref="tour",cascade="all, delete-orphan")
    # Define a method to calculate the price based on adults, kids, and private tour status
    def calculate_price(self, adults: int, kids: int, is_private: bool = False) -> float:
        """Calculate total price including private tour premium"""
        base_price = (adults + kids) * self.price
        return base_price * 1.35 if is_private else base_price
    
class TourImage(Base):
    __tablename__ = "tour_images"
    id = Column(Integer, primary_key=True, index=True)
    tour_id = Column(Integer, ForeignKey("tours.id"))
    image_url = Column(String(200))
    is_primary = Column(Boolean, default=False)
    
class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tour_id = Column(Integer, ForeignKey("tours.id"))
    adults = Column(Integer)
    kids = Column(Integer)
    tour_date = Column(DateTime)
    total_price = Column(Float)
    is_private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user= relationship("User", backref="bookings")
    tour= relationship("Tour", backref="bookings")
    payment_method = Column(String(20))
    payment_id = Column(String(50))
    payment_status = Column(String)
    @property
    def participant_count(self):
        return self.adults + self.kids