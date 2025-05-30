"""FastAPI Async IoT Box Proxy for Odoo (Printer)"""
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from hw_proxy.app.main import app_router

API_PREFIX = "/hw_proxy"

# --- App Initialization ---
app = FastAPI(
    title="Odoo IoT Box Proxy (FastAPI Async)",
    openapi_url=f"{API_PREFIX}/openapi.json",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc"
)

# --- CORS Middleware for Dev (allow all) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_router, prefix=API_PREFIX)