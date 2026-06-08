"""
CORA Database Layer
───────────────────
Async SQLAlchemy engine, session factory, and initialization.
Uses asyncpg as the PostgreSQL driver.
"""

from __future__ import annotations

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("cora.database")


# ── Declarative Base ─────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Engine & Session Factory (initialised at startup) ────────────────────────
_engine = None
_session_factory = None


def get_database_url() -> str:
    """Read DATABASE_URL from environment."""
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/cora",
    )
    return url


async def init_db() -> None:
    """
    Create the async engine, session factory, and all tables.
    Call this once at application startup.
    """
    global _engine, _session_factory

    url = get_database_url()
    logger.info(f"[CORA-DB] Connecting to: {url.split('@')[-1]}")  # log host only

    _engine = create_async_engine(
        url,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
    )

    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create all tables
    async with _engine.begin() as conn:
        import db_models  # noqa — ensure models are imported
        await conn.run_sync(Base.metadata.create_all)

    logger.info("[CORA-DB] Database initialized — tables created.")


async def close_db() -> None:
    """Close the engine and connection pool. Call at shutdown."""
    global _engine
    if _engine:
        await _engine.dispose()
        logger.info("[CORA-DB] Database connection closed.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency — yields an async DB session.

    Usage:
        @app.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
