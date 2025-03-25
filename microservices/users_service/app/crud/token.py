from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.token import UserToken
import time

def create_user_token(
    db: Session,
    user_id: int,
    access_token: str,
    device_info: str,
    ip_address: str,
    expires_at: int
) -> UserToken:
    """Create a new token record"""
    db_token = UserToken(
        uk_user_id=user_id,
        uk_access_token=access_token,
        uk_device_info=device_info,
        uk_ip_address=ip_address,
        uk_created_at=int(time.time()),
        uk_expires_at=expires_at,
        uk_is_active=1
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_token(db: Session, access_token: str) -> Optional[UserToken]:
    """Get token by access_token"""
    return db.query(UserToken).filter(
        UserToken.uk_access_token == access_token,
        UserToken.uk_is_active == 1
    ).first()

def get_user_tokens(db: Session, user_id: int) -> List[UserToken]:
    """Get all active tokens for a user"""
    return db.query(UserToken).filter(
        UserToken.uk_user_id == user_id,
        UserToken.uk_is_active == 1
    ).all()

def revoke_token(db: Session, access_token: str) -> bool:
    """Revoke a specific token"""
    token = get_token(db, access_token)
    if token:
        token.uk_is_active = 0
        db.commit()
        return True
    return False

def revoke_all_user_tokens(db: Session, user_id: int) -> bool:
    """Revoke all tokens for a user"""
    tokens = get_user_tokens(db, user_id)
    for token in tokens:
        token.uk_is_active = 0
    db.commit()
    return True

def cleanup_expired_tokens(db: Session) -> int:
    """Clean up expired tokens"""
    current_time = int(time.time())
    result = db.query(UserToken).filter(
        UserToken.uk_expires_at < current_time,
        UserToken.uk_is_active == 1
    ).update({"uk_is_active": 0})
    db.commit()
    return result 