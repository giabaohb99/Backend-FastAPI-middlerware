from fastapi import APIRouter
from .customer import router as customer_router
from .otp import router as otp_router

router = APIRouter()
router.include_router(customer_router, prefix="/customers", tags=["customers"])
router.include_router(otp_router, prefix="/otp", tags=["otp"]) 