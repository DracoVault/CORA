"""
CORA Authentication
───────────────────
Password hashing, session token management, and FastAPI auth dependencies.
"""

from __future__ import annotations

import uuid
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from db_models import User, UserSession

logger = logging.getLogger("cora.auth")

# ── Security scheme ─────────────────────────────────────────────────────────
security = HTTPBearer(auto_error=False)

# ── Session settings ────────────────────────────────────────────────────────
SESSION_DURATION_HOURS = 72  # sessions last 3 days


# ════════════════════════════════════════════════════════════════════════════════
#  PASSWORD HASHING
# ════════════════════════════════════════════════════════════════════════════════

def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ════════════════════════════════════════════════════════════════════════════════
#  SESSION TOKEN
# ════════════════════════════════════════════════════════════════════════════════

def create_session_token() -> str:
    """Generate a cryptographically secure session token (64 hex chars)."""
    return secrets.token_hex(32)


async def create_user_session(
    db: AsyncSession,
    user: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> UserSession:
    """Create a new session for a user and persist it."""
    session = UserSession(
        user_id=user.id,
        token=create_session_token(),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=SESSION_DURATION_HOURS),
        ip_address=ip_address,
        user_agent=user_agent,
        is_active=True,
    )
    db.add(session)
    await db.flush()

    # Update last_login
    user.last_login = datetime.now(timezone.utc)
    await db.flush()

    logger.info(f"Session created for user {user.username}")
    return session


async def invalidate_session(db: AsyncSession, token: str) -> bool:
    """Mark a session as inactive (logout)."""
    result = await db.execute(
        select(UserSession).where(UserSession.token == token)
    )
    session = result.scalar_one_or_none()
    if session:
        session.is_active = False
        await db.flush()
        return True
    return False


# ════════════════════════════════════════════════════════════════════════════════
#  FASTAPI DEPENDENCIES
# ════════════════════════════════════════════════════════════════════════════════

async def _resolve_user_from_token(
    token: str,
    db: AsyncSession,
) -> Optional[User]:
    """Look up a valid session token and return the associated user."""
    result = await db.execute(
        select(UserSession)
        .where(UserSession.token == token, UserSession.is_active == True)
    )
    session = result.scalar_one_or_none()

    if not session:
        return None

    if session.is_expired:
        session.is_active = False
        await db.flush()
        return None

    # Load user
    user_result = await db.execute(
        select(User).where(User.id == session.user_id, User.is_active == True)
    )
    return user_result.scalar_one_or_none()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency — requires a valid session token.
    Raises 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await _resolve_user_from_token(credentials.credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    FastAPI dependency — returns the authenticated user if a valid token
    is provided, or None for anonymous requests. Never raises 401.
    """
    if not credentials:
        return None

    return await _resolve_user_from_token(credentials.credentials, db)


async def get_current_session(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserSession]:
    """
    FastAPI dependency — returns the current session object if valid,
    or None for anonymous requests.
    """
    if not credentials:
        return None

    result = await db.execute(
        select(UserSession)
        .where(UserSession.token == credentials.credentials, UserSession.is_active == True)
    )
    session = result.scalar_one_or_none()

    if session and session.is_expired:
        session.is_active = False
        await db.flush()
        return None

    return session
