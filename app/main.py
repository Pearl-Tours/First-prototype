from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.routes import router
from app.database import engine, Base

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Middleware
app.add_middleware(SessionMiddleware, secret_key="your_secret_key", session_cookie="session_id")
#app.add_middleware(HTTPSRedirectMiddleware)

# Include routes
app.include_router(router)

# Create database tables
Base.metadata.create_all(bind=engine)
