"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api import network, scada, simulation
import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events."""
    # Startup: Initialize database
    try:
        await database.init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
        print("Database operations will fail until database is available")
    
    yield
    
    # Shutdown: Close database connections
    await database.close_db()

app = FastAPI(
    title="RTDWMS Backend",
    description="Real-Time Dynamic Water Network Monitoring System - Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(network.router)
app.include_router(scada.router)
app.include_router(simulation.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RTDWMS Backend API",
        "version": "1.0.0",
        "endpoints": {
            "network": "/api/network",
            "scada": "/api/scada"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

