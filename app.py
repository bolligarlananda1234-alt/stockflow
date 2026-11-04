
from fastapi import FastAPI

app = FastAPI(
    title="StockFlow API",
    description="SaaS Inventory Management System",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to StockFlow",
        "status": "Backend is running"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
