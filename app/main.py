
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.init_db import create_tables
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.routers.dashboard import router as dashboard_router

app = FastAPI(
    title="StockFlow API",
    description="SaaS Inventory Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    create_tables()

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(dashboard_router)

@app.get("/health")
def health():
    return {"status": "healthy"}

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend"
)
