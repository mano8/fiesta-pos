import os
import base64
import asyncio
from io import BytesIO
import time
from PIL import Image
from fastapi import FastAPI, Header, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from escpos.printer import Usb, Network, Serial, Dummy

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