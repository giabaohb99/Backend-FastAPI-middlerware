import logging
import json
from typing import Dict, Any, Optional
from fastapi import Request
from datetime import datetime

logger = logging.getLogger("activity_logger")

def log_customer_activity(
    request: Request,
    activity: str,
    customer_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Ghi log cho hoạt động của khách hàng
    
    Args:
        request: Request object hiện tại
        activity: Loại hoạt động (register, update, verify, etc.)
        customer_id: ID của customer (nếu có)
        details: Chi tiết thêm về hoạt động
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Chuẩn bị log data
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id,
        "activity": activity,
        "path": request.url.path,
        "method": request.method,
        "client_ip": client_ip,
        "user_agent": user_agent
    }
    
    if customer_id:
        log_data["customer_id"] = customer_id
    
    if details:
        # Sanitize sensitive information
        sanitized_details = {}
        sensitive_fields = ["password", "token", "secret", "key", "otp"]
        
        for key, value in details.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized_details[key] = "*****"
            else:
                sanitized_details[key] = value
                
        log_data["details"] = sanitized_details
    
    logger.info(f"Customer Activity: {json.dumps(log_data)}") 