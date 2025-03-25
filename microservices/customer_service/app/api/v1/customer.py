from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from op_core.core import get_db
from app.models.customer import Customer
from app.models.otp import OTPVerification, OTPType, OTPPurpose
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerRegisterRequest
from app.crud import customer as customer_crud
from app.crud import otp as otp_crud
from app.core.redis_client import redis_client
from app.core.email_utils import send_otp_email, generate_otp
from op_core.core import log_customer_activity
from op_core.core.config import settings
from app.core.user_client import UserClient, get_user_client

router = APIRouter()

@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    request: Request,
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all customers
    """
    customers = customer_crud.get_customers(db, skip=skip, limit=limit)
    return customers

@router.post("/", response_model=CustomerResponse)
def create_customer(
    request: Request,
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new customer (admin only)
    """
    db_customer = customer_crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Log customer creation
    log_customer_activity(
        request=request,
        activity="create_customer",
        details={"email": customer.email}
    )
    
    return customer_crud.create_customer(db=db, customer=customer)

@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register_customer(
    request: Request,
    customer: CustomerRegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_client: UserClient = Depends(get_user_client)
):
    """
    Register a new customer with OTP verification
    """
    # Check if email already exists
    db_customer = customer_crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this email already exists"
        )
    
    # Create a new user if needed
    try:
        user = await user_client.create_user(
            email=customer.email,
            full_name=customer.name
        )
      
        user_id = user["id"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )
    
    # Create customer with unverified status
    db_customer = Customer(
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        address=customer.address,
        user_id=user_id,
        is_verified=False
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    # # Create OTP verification record for database tracking
    # otp_record = OTPVerification(
    #     customer_id=db_customer.id,
    #     identifier=customer.email,
    #     otp_type=OTPType.EMAIL.value,
    #     otp_purpose=OTPPurpose.REGISTRATION.value
    # )
    # db.add(otp_record)
    # db.commit()
    # db.refresh(otp_record)
    
    # # Generate OTP
    # otp_code = generate_otp()
    
    # # Store OTP in Redis
    # redis_client.store_otp(customer.email, otp_code)
    
    # # Send OTP email
    # background_tasks.add_task(
    #     send_otp_email,
    #     email=customer.email,
    #     otp=otp_code,
    #     name=customer.name
    # )
    
    # # Log customer registration attempt
    # log_customer_activity(
    #     request=request,
    #     activity="register_customer",
    #     customer_id=db_customer.id,
    #     details={
    #         "email": customer.email,
    #         "verified": False
    #     }
    # )
    
    return {
        "message": "Registration initiated. Please check your email for verification code.",
        "customer_id": db_customer.id
    }

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    request: Request,
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get customer by ID
    """
    db_customer = customer_crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return db_customer

@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    request: Request,
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update customer
    """
    db_customer = customer_crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Log customer update
    log_customer_activity(
        request=request,
        activity="update_customer",
        customer_id=customer_id,
        details=customer.model_dump(exclude_unset=True)
    )
    
    return customer_crud.update_customer(db=db, customer_id=customer_id, customer=customer)

@router.delete("/{customer_id}", response_model=CustomerResponse)
def delete_customer(
    request: Request,
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete customer
    """
    db_customer = customer_crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Log customer deletion
    log_customer_activity(
        request=request,
        activity="delete_customer",
        customer_id=customer_id,
        details={"email": db_customer.email}
    )
    
    return customer_crud.delete_customer(db=db, customer_id=customer_id) 