import pytest
from unittest.mock import patch, MagicMock
from app.core.redis_client import store_otp, verify_otp, clear_otp

def test_store_otp():
    """Test storing OTP in Redis"""
    with patch('app.core.redis_client.redis_client') as mock_redis:
        # Setup the mock
        mock_redis.set.return_value = True
        
        # Call the function
        result = store_otp("test@example.com", "123456")
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called with expected arguments
        mock_redis.set.assert_called_once_with(
            "customer:otp:test@example.com", 
            "123456", 
            ex=300
        )

def test_verify_otp_valid():
    """Test verifying valid OTP"""
    with patch('app.core.redis_client.redis_client') as mock_redis:
        # Setup the mock
        mock_redis.get.return_value = "123456"
        
        # Call the function
        result = verify_otp("test@example.com", "123456")
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called with expected arguments
        mock_redis.get.assert_called_once_with("customer:otp:test@example.com")
        mock_redis.delete.assert_called_once_with("customer:otp:test@example.com")

def test_verify_otp_invalid():
    """Test verifying invalid OTP"""
    with patch('app.core.redis_client.redis_client') as mock_redis:
        # Setup the mock
        mock_redis.get.return_value = "123456"
        
        # Call the function with wrong OTP
        result = verify_otp("test@example.com", "654321")
        
        # Verify the result
        assert result is False
        
        # Verify the mock was called with expected arguments
        mock_redis.get.assert_called_once_with("customer:otp:test@example.com")
        # Delete should not be called for invalid OTP
        mock_redis.delete.assert_not_called()

def test_verify_otp_expired():
    """Test verifying expired OTP"""
    with patch('app.core.redis_client.redis_client') as mock_redis:
        # Setup the mock
        mock_redis.get.return_value = None
        
        # Call the function
        result = verify_otp("test@example.com", "123456")
        
        # Verify the result
        assert result is False
        
        # Verify the mock was called with expected arguments
        mock_redis.get.assert_called_once_with("customer:otp:test@example.com")
        mock_redis.delete.assert_not_called()

def test_clear_otp():
    """Test clearing OTP"""
    with patch('app.core.redis_client.redis_client') as mock_redis:
        # Setup the mock
        mock_redis.delete.return_value = 1
        
        # Call the function
        result = clear_otp("test@example.com")
        
        # Verify the result
        assert result is True
        
        # Verify the mock was called with expected arguments
        mock_redis.delete.assert_called_once_with("customer:otp:test@example.com") 