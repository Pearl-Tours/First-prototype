import pytest
from unittest.mock import MagicMock, patch
from app import utils
from types import SimpleNamespace
import bcrypt


def test_hash_and_verify_password():
    password = "securepassword"
    hashed = utils.hash_password(password)
    assert bcrypt.checkpw(password.encode(), hashed.encode())
    assert utils.verify_password(password, hashed)


def test_get_user_initials():
    user = SimpleNamespace(full_name="Jane Doe")
    assert utils.get_user_initials(user) == "JD"

    user.full_name = "John Ronald Reuel Tolkien"
    assert utils.get_user_initials(user) == "JRRT"

    user.full_name = ""
    assert utils.get_user_initials(user) == ""


def test_send_email(monkeypatch):
    mock_server = MagicMock()
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_server

    monkeypatch.setattr("smtplib.SMTP", lambda *args, **kwargs: mock_context)

    utils.send_email("test@example.com", "Test Subject", "Test Body")

    assert mock_server.starttls.called
    assert mock_server.login.called
    assert mock_server.send_message.called


def test_send_tour_notification(monkeypatch):
    sent = {}

    def fake_send_email(to_email, subject, body, is_html):
        sent['called'] = True
        sent['email'] = to_email
        sent['subject'] = subject
        sent['html'] = is_html

    monkeypatch.setattr(utils, "send_email", fake_send_email)

    tour = SimpleNamespace(
        title="Nile Cruise",
        description="Enjoy the longest river",
        price=120.0,
        duration="3 days",
        locations="Jinja"
    )
    utils.send_tour_notification("user@example.com", tour, "fake-token")
    assert sent['called'] is True
    assert sent['email'] == "user@example.com"
    assert "Nile Cruise" in sent['subject']
    assert sent['html'] is True