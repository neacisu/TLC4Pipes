"""
TLC4Pipe - Calculator Încărcare Țeavă HDPE
FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.routes import pipes, trucks, orders, calculations, reports, settings as settings_routes


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting TLC4Pipe API v{settings.VERSION}")
    print(f"📦 Debug mode: {settings.DEBUG}")
    yield
    # Shutdown
    print("👋 Shutting down TLC4Pipe API")


app = FastAPI(
    title="TLC4Pipe - Calculator Încărcare Țeavă HDPE",
    description="API pentru optimizarea încărcării țevilor HDPE în camioane",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker and load balancers."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": "tlc4pipe-backend",
    }


# API v1 Routers
app.include_router(pipes.router, prefix="/api/v1/pipes", tags=["Pipes"])
app.include_router(trucks.router, prefix="/api/v1/trucks", tags=["Trucks"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(calculations.router, prefix="/api/v1/calculations", tags=["Calculations"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(settings_routes.router, prefix="/api/v1/settings", tags=["Settings"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "TLC4Pipe API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else "Disabled in production",
    }
