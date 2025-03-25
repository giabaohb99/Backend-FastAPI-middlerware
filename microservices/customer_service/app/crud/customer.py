from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_
import random
import string
from ..models.customer import Customer
from ..schemas.customer import CustomerCreate, CustomerUpdate

def generate_customer_code() -> str:
    """Generate a unique customer code with format CUS-XXXXXXXX"""
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"CUS-{random_part}"

def get_customers(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all customers with optional search and pagination
    """
    query = db.query(Customer)
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Customer.full_name.ilike(search_term),
                Customer.email.ilike(search_term),
                Customer.phone.ilike(search_term),
                Customer.customer_code.ilike(search_term)
            )
        )
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination
    customers = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": customers,
        "page": skip // limit + 1 if limit else 1,
        "size": limit
    }

def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
    """
    Get a customer by ID
    """
    return db.query(Customer).filter(Customer.id == customer_id).first()

def get_customer_by_email(db: Session, email: str) -> Optional[Customer]:
    """
    Get a customer by email
    """
    return db.query(Customer).filter(Customer.email == email).first()

def get_customer_by_user_id(db: Session, user_id: int) -> Optional[Customer]:
    """
    Get a customer by user_id
    """
    return db.query(Customer).filter(Customer.user_id == user_id).first()

def get_customer_by_oauth_id(db: Session, provider: str, oauth_id: str) -> Optional[Customer]:
    """
    Get a customer by OAuth ID (Google, Facebook, or Yahoo)
    """
    if provider == "google":
        return db.query(Customer).filter(Customer.google_id == oauth_id).first()
    elif provider == "facebook":
        return db.query(Customer).filter(Customer.facebook_id == oauth_id).first()
    elif provider == "yahoo":
        return db.query(Customer).filter(Customer.yahoo_id == oauth_id).first()
    return None

def create_customer(db: Session, customer: Union[CustomerCreate, Dict[str, Any]]) -> Customer:
    """
    Create a new customer
    """
    # Generate a unique customer code
    customer_code = generate_customer_code()
    
    # Handle both dict and CustomerCreate
    if isinstance(customer, dict):
        customer_data = customer
    else:
        customer_data = customer.dict()
    
    # Create a new Customer object
    db_customer = Customer(
        customer_code=customer_code,
        full_name=customer_data.get("full_name", ""),
        email=customer_data.get("email", ""),
        phone=customer_data.get("phone"),
        birthdate=customer_data.get("birthdate"),
        address=customer_data.get("address"),
        user_id=customer_data.get("user_id"),
        google_id=customer_data.get("google_id"),
        facebook_id=customer_data.get("facebook_id"),
        yahoo_id=customer_data.get("yahoo_id")
    )
    
    # Add to DB and commit
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    return db_customer

def update_customer(db: Session, customer_id: int, customer: Union[CustomerUpdate, Dict[str, Any]]) -> Optional[Customer]:
    """
    Update an existing customer
    """
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None
    
    # Update only the fields that are provided
    if isinstance(customer, dict):
        update_data = customer
    else:
        update_data = customer.dict(exclude_unset=True)
        
    for key, value in update_data.items():
        setattr(db_customer, key, value)
    
    db.commit()
    db.refresh(db_customer)
    
    return db_customer

def delete_customer(db: Session, customer_id: int) -> bool:
    """
    Delete a customer
    """
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return False
    
    db.delete(db_customer)
    db.commit()
    
    return True 