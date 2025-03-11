from enum import IntEnum

class UserStatus(IntEnum):
    """User status enumeration"""
    DELETED = 0       # Tài khoản đã bị xóa
    ACTIVE = 1        # Tài khoản đang hoạt động
    SUSPENDED = 2     # Tài khoản bị tạm khóa
    PENDING = 3       # Tài khoản chờ xác thực
    BANNED = 4        # Tài khoản bị cấm vĩnh viễn
    INACTIVE = 5      # Tài khoản không hoạt động

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def get_description(cls, status):
        descriptions = {
            cls.DELETED: "Tài khoản đã bị xóa",
            cls.ACTIVE: "Tài khoản đang hoạt động",
            cls.SUSPENDED: "Tài khoản bị tạm khóa",
            cls.PENDING: "Tài khoản chờ xác thực",
            cls.BANNED: "Tài khoản bị cấm vĩnh viễn",
            cls.INACTIVE: "Tài khoản không hoạt động"
        }
        return descriptions.get(status, "Trạng thái không xác định") 