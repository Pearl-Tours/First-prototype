import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, User, Session, Tour, TourImage, Booking

# Setup in-memory SQLite test DB
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    yield db
    db.close()


def test_user_model_defaults(db):
    user = User(email="test@example.com", hashed_password="hashed", full_name="Test User")
    db.add(user)
    db.flush()
    assert user.is_active is True
    assert user.is_admin is False
    assert user.newsletter_subscribed is False
    assert isinstance(user.unsubscribe_token, str)


def test_session_model_defaults(db):
    session = Session(user_id=1)
    db.add(session)
    db.flush()
    assert isinstance(session.id, str)
    assert isinstance(session.created_at, datetime)


def test_tour_image_model(db):
    image = TourImage(tour_id=1, image_url="/images/tour.jpg")
    db.add(image)
    db.flush()
    assert image.is_primary is False
