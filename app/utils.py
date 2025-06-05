import bcrypt
import os
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models import User, Session, Tour
from fastapi import Request
from app.database import get_db
from typing import Optional


SESSION_EXPIRE_MINUTES = 30
load_dotenv()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_session(db: Session, user_id: int) -> str:
    # Delete existing sessions for the user
    db.query(Session).filter(Session.user_id == user_id).delete()
    
    # Create new session
    session = Session(
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(minutes=SESSION_EXPIRE_MINUTES)
    )
    db.add(session)
    db.commit()
    return session.id

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    session_id = request.cookies.get("auth_session_id")
    print(f"auth_Session ID from cookies: {session_id}")
    if not session_id:
        return None
    
    session = db.query(Session).filter(
        Session.id == session_id,
        Session.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        return None
    
    user = db.query(User).filter(User.id == session.user_id).first()
    print(f"Current user: {user}")
    return user

def delete_session(db: Session, session_id: str):
    db.query(Session).filter(Session.id == session_id).delete()
    db.commit()
    
def get_user_initials(user: User) -> str:
    if user.full_name:
        names = user.full_name.split()
        initials = ''.join([name[0].upper() for name in names])
        return initials
    return ''    

async def get_current_admin(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user(request, db)
    if not user or not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return user

async def send_email(to_email: str, subject: str, body: str):
    #smtp_server= "smtp.gmail.com"
    #smtp_port=587
    #smtp_user= "lubegarhyan639@gmail.com"
    #smtp_password= "fycogsnvnrkqsmfw"
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER", "default-email@example.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "default-password")

    # Email sending logic
    message = EmailMessage()
    message["From"] = smtp_user
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
            print(f"Email sent successfully to {to_email}")
            print("SMTP_USER:", os.getenv("SMTP_USER"))
            print("SMTP_PASSWORD:", os.getenv("SMTP_PASSWORD")) 

        
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {str(e)}")
        raise e  
        

async def get_authenticated_user(user: User = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            detail="Authentication required",
            headers={"Location": "/signup"}
        )
    return user

        
 
 
