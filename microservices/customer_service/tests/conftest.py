import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import get_db, Base
from app.models.customer import Customer
from app.models.otp import OTPVerification
from unittest.mock import patch, MagicMock

# Tạo database in-memory cho test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    """
    Tạo database session mới cho mỗi test function
    """
    # Tạo session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Tạo session mới
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        # Xóa hết dữ liệu sau mỗi test để test độc lập
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        db.close()

@pytest.fixture(scope="function")
def client(db_session):
    """
    Tạo test client với database session mới
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as client:
        yield client
    
    # Reset dependency overrides after test
    app.dependency_overrides = {}

@pytest.fixture(scope="function")
def mock_user_client():
    """
    Mock UserClient để không gọi user service thật
    """
    with patch("app.core.user_client.UserClient") as mock:
        user_client = MagicMock()
        # Mock create_user method
        user_client.create_user.return_value = {"id": 123, "email": "test@example.com"}
        mock.return_value = user_client
        yield user_client

@pytest.fixture(scope="function") 
def mock_email_sender():
    """
    Mock email sender để không gửi email thật
    """
    with patch("app.core.email_utils.send_otp_email") as mock:
        mock.return_value = None
        yield mock 