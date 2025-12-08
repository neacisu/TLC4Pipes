"""
Database Connection and Session Management
"""

import logging
import time

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.sql_echo_enabled,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

logger = logging.getLogger(__name__)


if settings.SLOW_QUERY_MS > 0:
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # noqa: ANN001, D401
        conn.info.setdefault("_query_start_time", []).append(time.perf_counter())

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):  # noqa: ANN001, D401
        start = conn.info.get("_query_start_time")
        if not start:
            return
        elapsed = (time.perf_counter() - start.pop()) * 1000
        if elapsed >= settings.SLOW_QUERY_MS:
            logger.warning(
                "db.slow_query",
                extra={"elapsed_ms": round(elapsed, 2), "statement": statement[:500]},
            )

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


async def get_db() -> AsyncSession:
    """
    Dependency for getting database session.
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
