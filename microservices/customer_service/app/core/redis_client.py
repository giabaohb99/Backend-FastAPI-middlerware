from op_core.core.redis_client import redis_client, get_redis
from op_core.core.config import settings

# Redis utility functions specific to customer service
def store_otp(email: str, otp: str, expiry_seconds: int = None):
    """
    Store OTP in Redis with expiration time (default from settings)
    
    Args:
        email: Customer email address
        otp: One-time password to store
        expiry_seconds: Time in seconds until OTP expires (default from settings)
    """
    if expiry_seconds is None:
        expiry_seconds = settings.OTP_EXPIRE_MINUTES * 60
        
    key = f"customer:otp:{email}"
    redis_client.set(key, otp, ex=expiry_seconds)
    return True

def verify_otp(email: str, otp: str) -> bool:
    """
    Verify if OTP is valid for the given email
    
    Args:
        email: Customer email address
        otp: One-time password to verify
        
    Returns:
        bool: True if OTP is valid, False otherwise
    """
    key = f"customer:otp:{email}"
    stored_otp = redis_client.get(key)
    
    if not stored_otp:
        return False
        
    # Check if OTP matches
    if stored_otp == otp:
        # Delete OTP after successful verification
        redis_client.delete(key)
        return True
        
    return False

def clear_otp(email: str):
    """
    Clear OTP for the given email
    
    Args:
        email: Customer email address
    """
    key = f"customer:otp:{email}"
    redis_client.delete(key)
    return True 