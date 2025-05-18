import sys
from app.database import SessionLocal
from app.models import User
from app.utils import hash_password

def create_admin():
    db = SessionLocal()
    
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    full_name = input("Enter admin full name: ")
    
    if db.query(User).filter(User.email == email).first():
        print("Admin user already exists!")
        sys.exit(1)
        
    admin = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        is_admin=True
    )
    
    db.add(admin)
    db.commit()
    print("Admin user created successfully!")

if __name__ == "__main__":
    create_admin()