"""
FastAPI Dependencies

Dependency injection for database sessions, authentication, and common utilities.
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session.
    
    Alias for get_db for clearer dependency injection.
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_database_session)):
            ...
    """
    async for session in get_db():
        yield session


def get_pagination_params(
    skip: int = 0,
    limit: int = 50
) -> dict:
    """
    Common pagination parameters.
    
    Usage:
        @router.get("/items")
        async def get_items(pagination: dict = Depends(get_pagination_params)):
            skip = pagination["skip"]
            limit = pagination["limit"]
    """
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip must be >= 0"
        )
    if limit < 1 or limit > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 200"
        )
    
    return {"skip": skip, "limit": limit}


def validate_pipe_length(pipe_length_m: float = 12.0) -> float:
    """
    Validate and return pipe length parameter.
    
    Valid lengths: 12.0, 12.5, 13.0 meters
    """
    valid_lengths = [12.0, 12.5, 13.0]
    
    if pipe_length_m not in valid_lengths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pipe length. Must be one of: {valid_lengths}"
        )
    
    return pipe_length_m


def validate_truck_config_id(truck_config_id: int = 1) -> int:
    """
    Validate truck configuration ID.
    """
    if truck_config_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid truck configuration ID"
        )
    
    return truck_config_id


# Common dependencies for easy import
__all__ = [
    "get_database_session",
    "get_pagination_params",
    "validate_pipe_length",
    "validate_truck_config_id",
]
