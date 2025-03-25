from enum import Enum, IntEnum

class CustomerStatus(IntEnum):
    """Enum for customer account status"""
    PENDING = 0      # Tài khoản đã đăng ký nhưng chưa xác thực OTP
    ACTIVE = 1       # Tài khoản đã xác thực OTP, đang hoạt động
    INACTIVE = 2     # Tài khoản đã bị vô hiệu hóa 
    LOCKED = 3       # Tài khoản đã bị khóa (do nhiều lần đăng nhập sai)
    DELETED = 4      # Tài khoản đã bị xóa

class OAuthProvider(str, Enum):
    """Enum for OAuth providers"""
    FACEBOOK = "facebook"
    GOOGLE = "google"
    YAHOO = "yahoo" 