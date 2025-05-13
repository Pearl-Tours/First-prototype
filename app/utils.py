import bcrypt
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models import User, Session, Tour
from app.database import get_db

SESSION_EXPIRE_MINUTES = 30

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
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None
    
    session = db.query(Session).filter(
        Session.id == session_id,
        Session.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        return None
    
    user = db.query(User).filter(User.id == session.user_id).first()
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

