import logging
import smtplib
import random
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from ..models.otp import OTPType, OTPPurpose
from ..crud import otp as otp_crud
from op_core.core.config import settings

logger = logging.getLogger(__name__)

def generate_otp(length: int = 6) -> str:
    """Generate a random numeric OTP code"""
    return ''.join(random.choices(string.digits, k=length))

def send_email(recipient: str, subject: str, body: str) -> bool:
    """
    Send email using SMTP
    """
    try:
        # Setup email
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_SENDER
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to SMTP server
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def send_otp_email(email: str, otp: str, name: str = "Customer") -> bool:
    """
    Send OTP verification email using Redis OTP
    
    Args:
        email: Recipient email
        otp: OTP code
        name: Customer name
    """
    subject = "Your Verification Code"
    
    # Create HTML email body
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4a90e2; color: white; padding: 10px 20px; text-align: center; }}
            .content {{ padding: 20px; border: 1px solid #ddd; }}
            .code {{ font-size: 24px; font-weight: bold; text-align: center; 
                    padding: 10px; margin: 20px 0; background-color: #f5f5f5; 
                    border-radius: 5px; letter-spacing: 5px; }}
            .footer {{ font-size: 12px; text-align: center; margin-top: 20px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Verification Code</h2>
            </div>
            <div class="content">
                <p>Hello {name},</p>
                <p>Please use the following verification code to complete your registration:</p>
                <div class="code">{otp}</div>
                <p>This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>This is an automated message, please do not reply to this email.</p>
                <p>&copy; {settings.PROJECT_NAME}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(recipient=email, subject=subject, body=body)

# Backwards compatibility function for existing code
async def send_otp_email_from_db(
    db: Session,
    recipient_email: str, 
    recipient_name: str, 
    otp_purpose: str = OTPPurpose.REGISTRATION.value,
    customer_id: int = None,
    device_info: str = None
) -> bool:
    """
    Generate OTP and send verification email using database OTP
    Kept for backward compatibility
    """
    # Tạo OTP mới
    otp_record = otp_crud.create_otp(
        db=db,
        identifier=recipient_email,
        otp_type=OTPType.EMAIL.value,
        otp_purpose=otp_purpose,
        customer_id=customer_id,
        device_info=device_info
    )
    
    # Send email with the OTP
    return send_otp_email(
        email=recipient_email,
        otp=otp_record.code,
        name=recipient_name
    )

def send_otp_sms(phone_number: str, otp: str, name: str = "Customer") -> bool:
    """
    Send OTP verification SMS
    This is a placeholder function - implement actual SMS sending logic here
    
    Args:
        phone_number: Phone number
        otp: OTP code
        name: Customer name
    
    Returns:
        bool: True if SMS was sent successfully, False otherwise
    """
    # This would typically integrate with an SMS service provider
    # For now, just log the message
    logger.info(f"SMS to {phone_number}: Your verification code is: {otp}")
    return True 