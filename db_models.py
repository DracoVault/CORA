"""
CORA Database Models
────────────────────
SQLAlchemy ORM models for users, sessions, and queries.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


# ── Helpers ──────────────────────────────────────────────────────────────────

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


# ════════════════════════════════════════════════════════════════════════════════
#  USER
# ════════════════════════════════════════════════════════════════════════════════

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    api_key_override = Column(String(500), nullable=True)  # optional per-user LLM key
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    queries = relationship("QueryRecord", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


# ════════════════════════════════════════════════════════════════════════════════
#  SESSION
# ════════════════════════════════════════════════════════════════════════════════

class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")
    queries = relationship("QueryRecord", back_populates="session")

    @property
    def is_expired(self) -> bool:
        return utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired

    def __repr__(self):
        return f"<Session {self.token[:8]}... user={self.user_id}>"


# ════════════════════════════════════════════════════════════════════════════════
#  QUERY RECORD
# ════════════════════════════════════════════════════════════════════════════════

class QueryRecord(Base):
    __tablename__ = "queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)

    # Request
    prompt = Column(Text, nullable=False)

    # Response
    response = Column(Text, nullable=True)
    model_used = Column(String(100), nullable=True)
    tier_assigned = Column(String(20), nullable=True)
    budget_score = Column(Integer, nullable=True)
    tokens_used = Column(Float, nullable=True)
    tokens_saved = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)

    # Cognitive analysis (full profile as JSON)
    cognitive_profile = Column(JSON, nullable=True)
    routing_reason = Column(Text, nullable=True)
    task_type = Column(String(30), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="queries")
    session = relationship("UserSession", back_populates="queries")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_queries_user_created", "user_id", "created_at"),
        Index("ix_queries_tier", "tier_assigned"),
        Index("ix_queries_created", "created_at"),
    )

    def __repr__(self):
        return f"<Query {str(self.id)[:8]}... tier={self.tier_assigned}>"
