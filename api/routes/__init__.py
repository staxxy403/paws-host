from fastapi import APIRouter()
from . import vps

routes_router = APIRouter()

routes_router.include_router(vps.router)
