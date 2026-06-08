"""
CORA Schemas
────────────
Pydantic request/response models for all API endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


# ════════════════════════════════════════════════════════════════════════════════
#  AUTH
# ════════════════════════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)

class LoginRequest(BaseModel):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=128)

class AuthResponse(BaseModel):
    token: str
    username: str
    user_id: str
    expires_at: str
    message: str = "Success"


# ════════════════════════════════════════════════════════════════════════════════
#  USER
# ════════════════════════════════════════════════════════════════════════════════

class UserProfileResponse(BaseModel):
    user_id: str
    username: str
    email: str
    created_at: str
    last_login: Optional[str] = None
    total_queries: int = 0
    total_tokens_saved: float = 0.0
    average_budget_score: float = 0.0
    top_task_type: Optional[str] = None

class UpdateProfileRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)

# ════════════════════════════════════════════════════════════════════════════════
#  QUERY
# ════════════════════════════════════════════════════════════════════════════════

class QueryRequest(BaseModel):
    prompt: str = Field(..., max_length=10000)
    user_api_key: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    model_used: str
    tier_assigned: str
    budget_score: int
    tokens_used: float
    tokens_saved: float
    latency_ms: float
    cognitive_profile: dict
    routing_reason: str

# ════════════════════════════════════════════════════════════════════════════════
#  PROMPT OPTIMIZATION
# ════════════════════════════════════════════════════════════════════════════════

class PromptOptimizeRequest(BaseModel):
    prompt: str = Field(..., max_length=10000)
    user_api_key: Optional[str] = None

class PromptMetrics(BaseModel):
    prompt: str
    tokens_used: float
    tokens_saved: float
    budget_score: int
    tier_assigned: str
    model_used: str

class PromptOptimizeResponse(BaseModel):
    original: PromptMetrics
    suggested: PromptMetrics

# ════════════════════════════════════════════════════════════════════════════════
#  COGNITIVE PROFILE
# ════════════════════════════════════════════════════════════════════════════════

class CognitiveProfileResponse(BaseModel):
    budget_score: int
    tier: str
    cognitive_profile: dict
    routing_reason: str
    task_type: str
    task_type_icon: str
    confidence: float


# ════════════════════════════════════════════════════════════════════════════════
#  STATS
# ════════════════════════════════════════════════════════════════════════════════

class StatsResponse(BaseModel):
    total_queries: int
    total_tokens_saved: float
    average_budget_score: float
    routing_distribution: dict


# ════════════════════════════════════════════════════════════════════════════════
#  QUERY HISTORY
# ════════════════════════════════════════════════════════════════════════════════

class QueryHistoryItem(BaseModel):
    id: str
    prompt: str
    response: Optional[str] = None
    model_used: Optional[str] = None
    tier_assigned: Optional[str] = None
    budget_score: Optional[int] = None
    tokens_used: Optional[float] = None
    tokens_saved: Optional[float] = None
    latency_ms: Optional[float] = None
    task_type: Optional[str] = None
    routing_reason: Optional[str] = None
    cognitive_profile: Optional[dict] = None
    created_at: str

class QueryHistoryResponse(BaseModel):
    queries: List[QueryHistoryItem]
    total: int
    page: int
    page_size: int
    has_more: bool
