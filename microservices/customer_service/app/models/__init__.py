from .customer import Customer
from .otp import OTPVerification, OTPType, OTPPurpose

# For alembic to detect models
__all__ = ["Customer", "OTPVerification", "OTPType", "OTPPurpose"] 