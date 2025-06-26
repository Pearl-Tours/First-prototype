import pytest
from unittest.mock import MagicMock, patch
from app import create_admin


# ✅ Simulate user input
@pytest.fixture
def mock_inputs(monkeypatch):
    inputs = iter([
        "admin@example.com",  # email
        "securepass123",      # password
        "Admin User"          # full name
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))


# ✅ Mock SessionLocal and DB behavior
@pytest.fixture
def mock_db(monkeypatch):
    # Fake query return that says user does not exist
    mock_user_query = MagicMock()
    mock_user_query.filter.return_value.first.return_value = None

    mock_db = MagicMock()
    mock_db.query.return_value = mock_user_query

    monkeypatch.setattr("app.create_admin.SessionLocal", lambda: mock_db)
    return mock_db


# ✅ Patch hash_password
@pytest.fixture(autouse=True)
def mock_hash(monkeypatch):
    monkeypatch.setattr("app.utils.hash_password", lambda pw: f"hashed-{pw}")


def test_create_admin_success(mock_inputs, mock_db, monkeypatch):
    # Avoid sys.exit from killing test
    monkeypatch.setattr("sys.exit", lambda code=0: (_ for _ in ()).throw(SystemExit(code)))

    with patch("builtins.print") as mock_print:
        try:
            create_admin.create_admin()
        except SystemExit:
            pass  # This is expected for exit(1) or exit(0)

        mock_print.assert_called_with("Admin user created successfully!")
        assert mock_db.add.called
        assert mock_db.commit.called


def test_create_admin_already_exists(monkeypatch):
    # Mock input
    inputs = iter(["admin@example.com", "securepass123", "Admin User"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Simulate user already exists
    mock_existing_user = MagicMock()
    mock_user_query = MagicMock()
    mock_user_query.filter.return_value.first.return_value = mock_existing_user

    mock_db = MagicMock()
    mock_db.query.return_value = mock_user_query
    monkeypatch.setattr("app.create_admin.SessionLocal", lambda: mock_db)

    # Prevent sys.exit from stopping the test
    monkeypatch.setattr("sys.exit", lambda code=0: (_ for _ in ()).throw(SystemExit(code)))

    with patch("builtins.print") as mock_print:
        with pytest.raises(SystemExit) as exc_info:
            create_admin.create_admin()

        mock_print.assert_called_with("Admin user already exists!")
        assert exc_info.value.code == 1
