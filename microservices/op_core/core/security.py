from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_SETTINGS["ACCESS_TOKEN_EXPIRE_MINUTES"])
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SETTINGS["SECRET_KEY"], algorithm=settings.JWT_SETTINGS["ALGORITHM"])
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    try:
        decoded_token = jwt.decode(token, settings.JWT_SETTINGS["SECRET_KEY"], algorithms=[settings.JWT_SETTINGS["ALGORITHM"]])
        return decoded_token
    except JWTError:
        return None 
def check_token_status(token: str) -> bool:
    
    return True