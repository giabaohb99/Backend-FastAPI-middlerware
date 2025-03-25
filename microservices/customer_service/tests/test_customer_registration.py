import pytest
from fastapi import status
from app.models.customer import Customer
from app.models.otp import OTPVerification
from app.core.redis_client import store_otp, verify_otp
from unittest.mock import patch

def test_register_customer_success(client, mock_email_sender, mock_user_client, db_session):
    """
    Test successful registration flow:
    1. Register customer
    2. Verify OTP
    """
    # Mock store_otp để không phải dùng Redis thật
    with patch('app.api.v1.customer.store_otp') as mock_store_otp:
        mock_store_otp.return_value = True
        
        # 1. Register customer
        register_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890",
            "address": "123 Test St"
        }
        
        response = client.post("/api/v1/customers/register", json=register_data)
        assert response.status_code == status.HTTP_202_ACCEPTED
        
        # Kiểm tra record trong database
        customer = db_session.query(Customer).filter(Customer.email == "test@example.com").first()
        assert customer is not None
        assert customer.is_verified == False
        assert customer.name == "Test User"
        
        # Kiểm tra customer_id được trả về
        assert "customer_id" in response.json()
        customer_id = response.json()["customer_id"]
        
        # Kiểm tra OTP record
        otp_record = db_session.query(OTPVerification).filter(
            OTPVerification.customer_id == customer_id
        ).first()
        assert otp_record is not None
        
        # Kiểm tra email được gọi
        mock_email_sender.assert_called_once()
        
    # 2. Verify OTP with mock verify_otp
    with patch('app.api.v1.otp.verify_otp') as mock_verify_otp:
        mock_verify_otp.return_value = True
        
        verification_data = {
            "email": "test@example.com",
            "otp": "123456"  # Mock OTP
        }
        
        response = client.post("/api/v1/otp/verify", json=verification_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Kiểm tra customer đã được verify
        db_session.refresh(customer)
        assert customer.is_verified == True

def test_register_customer_duplicate_email(client, mock_email_sender, mock_user_client, db_session):
    """
    Test registration with duplicate email
    """
    # Tạo customer trước
    customer = Customer(
        name="Existing User",
        email="test@example.com",
        phone="1234567890",
        address="123 Test St",
        is_verified=True
    )
    db_session.add(customer)
    db_session.commit()
    
    # Thử register với email đã tồn tại
    register_data = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "9876543210",
        "address": "456 Test St"
    }
    
    response = client.post("/api/v1/customers/register", json=register_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()

def test_verify_otp_invalid(client, mock_email_sender, db_session):
    """
    Test OTP verification with invalid OTP
    """
    # Create customer
    customer = Customer(
        name="Test User",
        email="test@example.com",
        phone="1234567890",
        address="123 Test St",
        is_verified=False
    )
    db_session.add(customer)
    db_session.commit()
    
    # Mock verify_otp to return False (invalid OTP)
    with patch('app.api.v1.otp.verify_otp') as mock_verify_otp:
        mock_verify_otp.return_value = False
        
        verification_data = {
            "email": "test@example.com",
            "otp": "wrong_otp"
        }
        
        response = client.post("/api/v1/otp/verify", json=verification_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "invalid" in response.json()["detail"].lower()
        
        # Customer should still be unverified
        db_session.refresh(customer)
        assert customer.is_verified == False

def test_resend_otp(client, mock_email_sender, db_session):
    """
    Test resending OTP
    """
    # Create customer
    customer = Customer(
        name="Test User",
        email="test@example.com",
        phone="1234567890",
        address="123 Test St",
        is_verified=False
    )
    db_session.add(customer)
    db_session.commit()
    
    # Create OTP record
    otp = OTPVerification(
        customer_id=customer.id,
        email=customer.email
    )
    db_session.add(otp)
    db_session.commit()
    
    # Mock store_otp để không dùng Redis thật
    with patch('app.api.v1.otp.store_otp') as mock_store_otp:
        mock_store_otp.return_value = True
        
        # Request to resend OTP
        resend_data = {
            "email": "test@example.com"
        }
        
        response = client.post("/api/v1/otp/resend", json=resend_data)
        assert response.status_code == status.HTTP_200_OK
        
        # Kiểm tra email được gọi
        mock_email_sender.assert_called_once()
        
        # Kiểm tra Redis OTP được tạo
        mock_store_otp.assert_called_once() 