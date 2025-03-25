from typing import Optional, Dict, Any
import httpx
from pydantic import BaseModel
import json
import sys
from pprint import pprint
from op_core.core.debug import debug_request, debug_response, debug_error
from fastapi import HTTPException, status


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class UserClient:
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}" if token else ""
        }
        self.timeout = 30.0  # 30 seconds timeout

    async def health_check(self) -> bool:
        """
        Check if user service is available
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return True
            except Exception as e:
                debug_error(e)
                return False

    async def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Tạo user mới và trả về thông tin user bao gồm ID
        """
        async with httpx.AsyncClient() as client:
            try:
             
                response = await client.post(
                    f"http://host.docker.internal:8000/api/v1/user/register",
                    json=user_data.dict(),
                    headers=self.headers,
                    timeout=self.timeout
                )
         
                response.raise_for_status()
                return response.json()
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="User service request timeout"
                )
            except httpx.ConnectError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="User service is not available"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Lấy thông tin user theo ID
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/users/{user_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Dict[str, Any]:
        """
        Cập nhật thông tin user
        """
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/api/v1/users/{user_id}",
                json=user_data.dict(exclude_unset=True),
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def delete_user(self, user_id: int) -> None:
        """
        Xóa user
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api/v1/users/{user_id}",
                headers=self.headers
            )
            response.raise_for_status()

    async def verify_otp(self, user_id: int, otp: str) -> Dict[str, Any]:
        """
        Xác thực OTP cho user
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/users/{user_id}/verify-otp",
                json={"otp": otp},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def resend_otp(self, user_id: int) -> Dict[str, Any]:
        """
        Gửi lại OTP cho user
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/users/{user_id}/resend-otp",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def verify_credentials(self, username: str, password: str) -> Dict[str, Any]:
        """
        Verify user credentials
        """
        async with httpx.AsyncClient() as client:
            try:
                # Debug request
                debug_request(
                    method="POST",
                    url=f"{self.base_url}/api/v1/users/verify",
                    headers=self.headers,
                    data={
                        "username": username,
                        "password": "***"  # Hide password in debug
                    }
                )
                
                response = await client.post(
                    f"{self.base_url}/api/v1/users/verify",
                    json={"username": username, "password": password},
                    headers=self.headers
                )
                
                # Debug response
                debug_response(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=response.json()
                )
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                debug_error(e)
                raise 