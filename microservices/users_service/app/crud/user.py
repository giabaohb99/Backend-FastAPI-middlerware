from sqlalchemy.orm import Session
from typing import Optional
from op_core.core import get_password_hash, verify_password
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.constants import UserStatus
import time

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.u_id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.u_email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.u_email == username).first()  # Using email as username

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        u_email=user.email,
        u_password=hashed_password,
        u_fullname=user.full_name,
        u_status=user.status,
        u_datecreated=int(time.time()),
        u_datemodified=int(time.time())
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    
    # Map the fields to database column names
    field_mapping = {
        "email": "u_email",
        "password": "u_password",
        "full_name": "u_fullname",
        "status": "u_status"
    }
    
    for field, value in update_data.items():
        if field == "password":
            setattr(db_user, "u_password", get_password_hash(value))
        else:
            db_field = field_mapping.get(field)
            if db_field:
                setattr(db_user, db_field, value)
    
    # Update modified time
    db_user.u_datemodified = int(time.time())
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    user.u_status = UserStatus.DELETED  # Set status to deleted
    user.u_datemodified = int(time.time())
    db.commit()
    return True

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.u_password):
        return None
    if user.u_status != UserStatus.ACTIVE:  # Check if user is active
        return None
        
    # Update last login time
    user.u_datelastlogin = int(time.time())
    user.u_datemodified = int(time.time())
    db.commit()
    
    return user 