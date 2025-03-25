from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Any, List
import time
from op_core.core import get_db, create_access_token, settings
from ...crud.user import (
    authenticate_user, create_user, get_user_by_email, 
    get_user_by_username, get_users, get_user_by_id,
    update_user, delete_user
)
from ...crud.token import create_user_token, revoke_token, get_user_tokens , get_token
from ...schemas.user import User, UserCreate, UserUpdate, Token, UserLogin , UserLogout
from ...core.constants import UserStatus

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Authentication endpoints
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    Register new user.
    """
    try:
        user = get_user_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email already registered"
            )
        
        # user = get_user_by_username(db, username=user_in.username)
        # if user:
        #     raise HTTPException(
        #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        #         detail="Username already registered"
        #     )
        
        user = create_user(db, user_in)
        db.commit()
        return user
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while registering user: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """
    Login with username and password, get an access token for future requests.
    """
    try:
        user_data = await request.json()
        login_data = UserLogin(**user_data)
        user = authenticate_user(db, login_data.username, login_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"User account is {UserStatus.get_description(user.status).lower()}"
            )
        
        access_token_expires = timedelta(minutes=settings.JWT_SETTINGS["ACCESS_TOKEN_EXPIRE_MINUTES"])
        expires_at = int(time.time() + access_token_expires.total_seconds())
        
        token_data = {
            "sub": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "status": user.status,
            "ip_address": request.client.host,
            "timestamp": int(time.time())
        }
        
        access_token = create_access_token(
            data=token_data, expires_delta=access_token_expires
        )

        # Get client info
        client_host = request.client.host
        user_agent = request.headers.get("user-agent", "Unknown")

        # Create token record
        token_created = create_user_token(
            db=db,
            user_id=user.id,
            access_token=access_token,
            device_info=user_agent,
            ip_address=client_host,
            expires_at=expires_at
        )
        if not token_created:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating access token"
            )

        # Update last login time
        user.u_datelastlogin = int(time.time())
        db.commit()

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}"
        )

# Token management endpoints
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """
    Logout user by revoking the current token
    """
    try:
        user_data = await  request.json()
        logout_data = UserLogout(**user_data)
        success = revoke_token(db, logout_data.token)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        return {"message": "Successfully logged out"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during logout: {str(e)}"
        )

@router.get("/user/sessions", response_model=List[dict])
def get_user_sessions(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Any:
    """
    Get all active sessions for the current user
    """
    try:
        # Get current user's ID from token
        current_token = get_token(db, token)
        if not current_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        tokens = get_user_tokens(db, current_token.user_id)
        return [{
            "device_info": t.device_info,
            "ip_address": t.ip_address,
            "created_at": datetime.fromtimestamp(t.created_at),
            "expires_at": datetime.fromtimestamp(t.expires_at),
            "is_current": t.access_token == token
        } for t in tokens]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving sessions: {str(e)}"
        )

# User management endpoints
@router.get("/users", response_model=List[User])
def list_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(oauth2_scheme)
) -> Any:
    """
    Retrieve users.
    """
    try:
        users = get_users(db, skip=skip, limit=limit)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving users: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Any:
    """
    Get user by ID.
    """
    try:
        user = get_user_by_id(db, user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving user: {str(e)}"
        )

@router.put("/users/{user_id}", response_model=User)
def update_user_info(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Any:
    """
    Update user.
    """
    try:
        user = update_user(db, user_id=user_id, user=user_in)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        db.commit()
        return user
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating user: {str(e)}"
        )

@router.delete("/users/{user_id}", response_model=bool)
def delete_user_account(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Any:
    """
    Delete user.
    """
    try:
        success = delete_user(db, user_id=user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        db.commit()
        return success
    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting user: {str(e)}"
        ) 