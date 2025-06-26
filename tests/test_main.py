import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_static_files_served():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/static/")
        # We expect 403 or 404 because we're accessing the root of static without a file
        assert response.status_code in {403, 404}


@pytest.mark.asyncio
async def test_router_root():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "Pearl Tours" in response.text


def test_app_has_middlewares():
    middleware_names = [middleware.cls.__name__ for middleware in app.user_middleware]
    assert "SessionMiddleware" in middleware_names
    # assert "HTTPSRedirectMiddleware" not in middleware_names (uncomment if not using it)


def test_app_routes_registered():
    route_paths = [route.path for route in app.router.routes]
    assert "/" in route_paths
    assert any(path.startswith("/tours") for path in route_paths)
