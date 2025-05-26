"""FastAPI Async IoT Box Proxy for Odoo (Printer)"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from hw_proxy.app.main import app_router

# --- App Initialization ---
app = FastAPI(title="Odoo IoT Box Proxy (FastAPI Async)")

# --- CORS Middleware for Dev (allow all) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_router)