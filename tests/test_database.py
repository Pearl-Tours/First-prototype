import pytest
from sqlalchemy import text
from app.database import get_db, SessionLocal
from sqlalchemy.orm import Session

def test_get_db_yields_session():
    # Ensure get_db yields a SQLAlchemy session and closes it after use
    generator = get_db()
    db = next(generator)

    assert isinstance(db, Session)  # It should be a SQLAlchemy session
    assert db.is_active is True     # Active session while yielded

    # Close the session (simulate exiting the context)
    try:
        next(generator)
    except StopIteration:
        pass

    # Use SQLAlchemy's text() for raw SQL execution
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        pytest.fail("Session appears to be unusable after generator exit")


def test_sessionlocal_instance():
    session = SessionLocal()
    assert isinstance(session, Session)
    session.close()