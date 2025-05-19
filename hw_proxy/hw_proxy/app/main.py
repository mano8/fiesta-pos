from fastapi import APIRouter

from hw_proxy.app.routes import hw_proxy


app_router = APIRouter()
app_router.include_router(hw_proxy.router)