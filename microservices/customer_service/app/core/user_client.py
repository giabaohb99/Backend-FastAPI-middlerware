from typing import Optional, Dict, Any
from op_core.rest.user.client import UserClient as BaseUserClient, UserCreate
import os
from op_core.core.config import settings

class UserClient:
    """
    Client for user service.
    This is a wrapper around the op_core.rest.user.client.UserClient
    to make it easier to use in this service.
    """
    def __init__(self):
        self.user_service_url = settings.SERVICES["customers"]["api_prefix"]
        self.client = BaseUserClient(base_url=self.user_service_url)

    async def create_user(self, email: str, full_name: str, password: str = "123456") -> Dict[str, Any]:
        """
        Create a new user with a default password.
        """
        user_data = UserCreate(
            username=email,  # Using email as username
            email=email,
            password=password,
            full_name=full_name
        )
        
        return await self.client.create_user(user_data)
    
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Get a user by ID.
        """
        return await self.client.get_user(user_id)

# Dependency to get a UserClient instance
def get_user_client() -> UserClient:
    return UserClient() 