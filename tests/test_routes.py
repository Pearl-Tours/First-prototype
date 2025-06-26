import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from app.main import app  # Your FastAPI app instance


@pytest.mark.asyncio
async def test_read_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "Pearl Tours" in response.text


@pytest.mark.asyncio
async def test_get_signup():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/signup")
    assert response.status_code == 200
    assert "Sign" in response.text  # Basic content check


@pytest.mark.asyncio
async def test_get_login():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/login")
    assert response.status_code == 200
    assert "Login" in response.text  # Assumes template contains this


@pytest.mark.asyncio
async def test_show_cultures():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/cultures")
    assert response.status_code == 200
    assert "Central Region" in response.text  # Content from hardcoded `regions`


# Add more endpoint tests here for routes that do not require auth/db
# e.g., forgot-password GET, reset-password GET, newsletter GET


@pytest.mark.asyncio
async def test_forgot_password_form():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/forgot-password")
    assert response.status_code == 200
    assert "Forgot Password" in response.text  # assuming the template has this


@pytest.mark.asyncio
async def test_show_reset_password_form_invalid_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/reset-password?token=invalid")
    assert response.status_code == 200
    assert "Invalid or expired token" in response.text


# Note: Routes with DB/session/auth interaction need advanced mocking or test DB.
# Consider using a test database, dependency override, and factory boy for those.

# Example for future:
# app.dependency_overrides[get_db] = override_get_test_db
