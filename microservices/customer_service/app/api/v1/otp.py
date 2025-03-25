from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from op_core.core import get_db
from app.core.email_utils import send_otp_email, generate_otp
from app.models.otp import OTPType, OTPPurpose
from app.schemas.otp import OTPVerifyRequest, OTPResendRequest, OTPResponse
from app.crud import otp as otp_crud
from app.crud import customer as customer_crud
from op_core.core import log_customer_activity
from app.core.redis_client import store_otp, verify_otp, clear_otp
from op_core.core.redis_client import redis_client
from op_core.core.config import settings

router = APIRouter()

@router.post("/verify", response_model=OTPResponse)
async def verify_otp_endpoint(
    request: Request,
    verification_data: OTPVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Xác thực mã OTP
    """
    # Kiểm tra OTP từ Redis
    email = verification_data.email
    otp_code = verification_data.otp
    
    is_valid = verify_otp(email, otp_code)
    
    if not is_valid:
        # Log OTP verification failure
        customer = customer_crud.get_customer_by_email(db, email)
        
        log_details = {
            "email": email,
            "success": False
        }
        
        log_customer_activity(
            request=request,
            activity="verify_otp_failed",
            customer_id=customer.id if customer else None,
            details=log_details
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code or OTP has expired."
        )
    
    # OTP is valid, update customer status
    customer = customer_crud.get_customer_by_email(db, email)
    if customer:
        # Set customer as verified
        customer_crud.update_customer(db, customer.id, {"is_verified": True})
        
        # Log OTP verification success
        log_customer_activity(
            request=request,
            activity="verify_otp",
            customer_id=customer.id,
            details={
                "email": email,
                "verified": True
            }
        )
        
        return {"success": True, "message": "OTP verification successful"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

@router.post("/resend", response_model=OTPResponse)
async def resend_otp(
    request: Request,
    request_data: OTPResendRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Gửi lại OTP qua email
    """
    email = request_data.email
    
    # Kiểm tra customer có tồn tại không
    customer = customer_crud.get_customer_by_email(db, email)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Kiểm tra tần suất yêu cầu OTP
    key = f"otp:resend_limit:{email}"
    
    # Thử lấy số lần đã yêu cầu OTP
    attempts = redis_client.get(key)
    
    if attempts and int(attempts) >= settings.OTP_MAX_RESENDS:
        # Log OTP request rate limit
        log_customer_activity(
            request=request,
            activity="otp_rate_limited",
            customer_id=customer.id,
            details={
                "email": email
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many OTP requests. Please wait {settings.OTP_COOLDOWN_MINUTES} minutes before requesting again."
        )
    
    # Tăng số lần yêu cầu OTP và đặt thời gian hết hạn
    if attempts:
        redis_client.incr(key)
    else:
        redis_client.set(key, 1, ex=settings.OTP_COOLDOWN_MINUTES * 60)
    
    # Tạo OTP mới
    otp_code = generate_otp()
    
    # Lưu OTP vào Redis
    store_otp(email, otp_code, settings.OTP_EXPIRE_MINUTES * 60)
    
    # Gửi OTP trong background task
    background_tasks.add_task(
        send_otp_email,
        email=email,
        otp=otp_code,
        name=customer.name
    )
    
    # Log OTP send activity
    log_customer_activity(
        request=request,
        activity="send_otp_email",
        customer_id=customer.id,
        details={
            "email": email
        }
    )
    
    return {
        "success": True,
        "message": f"OTP has been sent to {email}. Please check your inbox."
    }

@router.get("/clean-expired", response_model=Dict[str, Any])
async def clean_expired_otps(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Xóa các OTP đã hết hạn (chỉ dành cho admin)
    """
    count = otp_crud.clean_expired_otps(db)
    
    # Log cleanup activity
    log_customer_activity(
        request=request,
        activity="clean_expired_otps",
        details={"count": count}
    )
    
    return {
        "success": True,
        "message": f"Đã xóa {count} OTP đã hết hạn."
    } 