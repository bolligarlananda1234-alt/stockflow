
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.routers.dashboard import router as dashboard_router

app = FastAPI(
    title="StockFlow API",
    description="SaaS Inventory Management System",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(dashboard_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to StockFlow",
        "status": "Backend is running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
