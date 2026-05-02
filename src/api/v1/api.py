from fastapi import APIRouter

from src.api.v1.endpoints import masjids
from src.api.v1.endpoints import auth
from src.api.v1.endpoints import income
from src.api.v1.endpoints import expense
from src.api.v1.endpoints import accounts

api_router = APIRouter()
api_router.include_router(masjids.router, prefix="/masjids", tags=["masjids"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(income.router, prefix="/income", tags=["income"])
api_router.include_router(expense.router, prefix="/expense", tags=["expense"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
