"""
TLC4Pipe - Calculator Încărcare Țeavă HDPE
FastAPI Application Entry Point
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.api.v1.routes import pipes, trucks, orders, calculations, reports, settings as settings_routes
from app.logging_config import setup_logging, set_request_id, get_request_id
from database.connection import engine


logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    setup_logging(
        level=settings.effective_log_level,
        enable_sql=settings.sql_echo_enabled,
        log_file=settings.LOG_FILE,
    )
    start = time.perf_counter()
    logger.info("Starting TLC4Pipe API", extra={"version": settings.VERSION, "debug": settings.DEBUG})
    try:
        yield
    finally:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info("Shutting down TLC4Pipe API", extra={"uptime_ms": duration_ms})


app = FastAPI(
    title="TLC4Pipe - Calculator Încărcare Țeavă HDPE",
    description="API pentru optimizarea încărcării țevilor HDPE în camioane",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Attach request id and log basic request/response data."""
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    set_request_id(request_id)

    start_time = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        # Let exception handlers manage logging
        raise

    process_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request.completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": process_ms,
            "client": request.client.host if request.client else None,
            "request_id": request_id,
            "content_length": request.headers.get("content-length"),
        },
    )

    set_request_id(None)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        "http_exception",
        extra={
            "path": request.url.path,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "request_id": get_request_id(),
        },
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        "validation_error",
        extra={
            "path": request.url.path,
            "errors": exc.errors(),
            "body": request.method,
            "request_id": get_request_id(),
        },
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        exc_info=exc,
        extra={
            "path": request.url.path,
            "method": request.method,
            "request_id": get_request_id(),
        },
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

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
    started = time.perf_counter()
    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception as exc:  # pragma: no cover - health failure path
        logger.error("db_health_check_failed", exc_info=exc)

    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    logger.info("health_check", extra={"db_ok": db_ok, "duration_ms": duration_ms})

    status = "healthy" if db_ok else "degraded"
    return {
        "status": status,
        "version": settings.VERSION,
        "service": "tlc4pipe-backend",
        "db": db_ok,
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
