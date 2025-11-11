from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app import models
from app.config import settings
from app.routers import customers, invoices, analytics

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(customers.router)
app.include_router(invoices.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "healthy",
        "service": settings.app_name
    }

