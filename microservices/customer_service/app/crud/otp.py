from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
import random
import string
from op_core.core.config import settings
from ..models.otp import OTPVerification, OTPType, OTPPurpose
from ..schemas.otp import OTPCreate

def generate_otp(length: int = None) -> str:
    """
    Generate a random OTP code
    """
    if length is None:
        length = settings.OTP_LENGTH
    return ''.join(random.choices(string.digits, k=length))

def create_otp(
    db: Session, 
    identifier: str, 
    otp_type: str, 
    otp_purpose: str, 
    customer_id: Optional[int] = None,
    device_info: Optional[str] = None
) -> OTPVerification:
    """
    Tạo mới một mã OTP
    """
    # Tính thời gian hết hạn
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    
    # Tạo mã OTP
    otp_code = generate_otp()
    
    # Kiểm tra xem đã có OTP cho identifier này chưa và chưa hết hạn
    existing_otp = db.query(OTPVerification).filter(
        and_(
            OTPVerification.identifier == identifier,
            OTPVerification.otp_type == otp_type,
            OTPVerification.otp_purpose == otp_purpose,
            OTPVerification.expires_at > datetime.utcnow(),
            OTPVerification.is_used == False
        )
    ).first()
    
    if existing_otp:
        # Cập nhật OTP hiện có
        existing_otp.code = otp_code
        existing_otp.expires_at = expires_at
        existing_otp.is_sent = False
        existing_otp.send_count += 1
        existing_otp.verify_count = 0
        db.commit()
        db.refresh(existing_otp)
        return existing_otp
    
    # Tạo OTP mới
    otp = OTPVerification(
        identifier=identifier,
        otp_type=otp_type,
        otp_purpose=otp_purpose,
        code=otp_code,
        expires_at=expires_at,
        customer_id=customer_id,
        device_info=device_info
    )
    
    db.add(otp)
    db.commit()
    db.refresh(otp)
    
    return otp

def get_otp(
    db: Session, 
    identifier: str, 
    code: str, 
    otp_type: str, 
    otp_purpose: str
) -> Optional[OTPVerification]:
    """
    Lấy thông tin OTP dựa trên identifier, code, type và purpose
    """
    return db.query(OTPVerification).filter(
        and_(
            OTPVerification.identifier == identifier,
            OTPVerification.code == code,
            OTPVerification.otp_type == otp_type,
            OTPVerification.otp_purpose == otp_purpose,
            OTPVerification.expires_at > datetime.utcnow(),
            OTPVerification.is_used == False
        )
    ).first()

def get_latest_otp(
    db: Session, 
    identifier: str, 
    otp_type: str, 
    otp_purpose: str
) -> Optional[OTPVerification]:
    """
    Lấy OTP mới nhất cho một identifier
    """
    return db.query(OTPVerification).filter(
        and_(
            OTPVerification.identifier == identifier,
            OTPVerification.otp_type == otp_type,
            OTPVerification.otp_purpose == otp_purpose,
            OTPVerification.expires_at > datetime.utcnow(),
            OTPVerification.is_used == False
        )
    ).order_by(desc(OTPVerification.created_at)).first()

def mark_otp_sent(db: Session, otp_id: int) -> Optional[OTPVerification]:
    """
    Đánh dấu OTP đã được gửi
    """
    otp = db.query(OTPVerification).filter(OTPVerification.id == otp_id).first()
    if otp:
        otp.is_sent = True
        otp.send_count += 1
        db.commit()
        db.refresh(otp)
    return otp

def mark_otp_used(db: Session, otp_id: int) -> Optional[OTPVerification]:
    """
    Đánh dấu OTP đã được sử dụng
    """
    otp = db.query(OTPVerification).filter(OTPVerification.id == otp_id).first()
    if otp:
        otp.is_used = True
        db.commit()
        db.refresh(otp)
    return otp

def increment_verify_count(db: Session, otp_id: int) -> Optional[OTPVerification]:
    """
    Tăng số lần đã thử xác thực
    """
    otp = db.query(OTPVerification).filter(OTPVerification.id == otp_id).first()
    if otp:
        otp.verify_count += 1
        db.commit()
        db.refresh(otp)
    return otp

def validate_otp(
    db: Session, 
    identifier: str, 
    code: str, 
    otp_type: str, 
    otp_purpose: str
) -> Dict[str, Any]:
    """
    Xác thực mã OTP từ database (Không dùng Redis)
    """
    # Lấy OTP từ database
    otp = get_otp(db, identifier, code, otp_type, otp_purpose)
    
    # Nếu không tìm thấy OTP
    if not otp:
        # Tìm OTP mới nhất cho identifier này để tăng số lần thử
        latest_otp = get_latest_otp(db, identifier, otp_type, otp_purpose)
        if latest_otp:
            increment_verify_count(db, latest_otp.id)
            
            # Kiểm tra nếu đã vượt quá số lần thử
            if latest_otp.verify_count >= settings.OTP_MAX_ATTEMPTS:
                # Ghi log vào Redis
                from op_core.core.redis_client import redis_client
                failed_key = f"otp:failed:{identifier}"
                redis_client.incr(failed_key)
                redis_client.expire(failed_key, settings.OTP_COOLDOWN_MINUTES * 60)
                
                return {
                    "success": False,
                    "message": f"Đã vượt quá số lần thử tối đa ({settings.OTP_MAX_ATTEMPTS}). Vui lòng yêu cầu mã OTP mới.",
                    "data": {"exceeded_attempts": True}
                }
        
        return {
            "success": False,
            "message": "Mã OTP không đúng hoặc đã hết hạn.",
            "data": None
        }
    
    # Tăng số lần thử
    increment_verify_count(db, otp.id)
    
    # Kiểm tra nếu đã vượt quá số lần thử
    if otp.verify_count > settings.OTP_MAX_ATTEMPTS:
        # Ghi log vào Redis
        from op_core.core.redis_client import redis_client
        failed_key = f"otp:failed:{identifier}"
        redis_client.incr(failed_key)
        redis_client.expire(failed_key, settings.OTP_COOLDOWN_MINUTES * 60)
        
        return {
            "success": False,
            "message": f"Đã vượt quá số lần thử tối đa ({settings.OTP_MAX_ATTEMPTS}). Vui lòng yêu cầu mã OTP mới.",
            "data": {"exceeded_attempts": True}
        }
    
    # Đánh dấu là đã sử dụng
    mark_otp_used(db, otp.id)
    
    return {
        "success": True,
        "message": "Xác thực OTP thành công.",
        "data": {"otp": otp}
    }

def clean_expired_otps(db: Session) -> int:
    """
    Xóa các OTP đã hết hạn
    """
    expired_otps = db.query(OTPVerification).filter(
        OTPVerification.expires_at <= datetime.utcnow()
    ).all()
    
    count = len(expired_otps)
    
    for otp in expired_otps:
        db.delete(otp)
    
    db.commit()
    
    return count 