"""
cognitive_module
────────────────
Standalone cognitive analysis package for CORA.

Public API:
    from cognitive_module import create_scorer, CognitiveProfile, TaskType

    scorer = create_scorer()                     # auto (defaults to nemo)
    scorer = create_scorer("rule")               # force rule-based
    scorer = create_scorer("nemo")               # force NVIDIA NeMo inference
    scorer = create_scorer("ml")                 # force DistilBERT
    
    profile = scorer.score("Explain how ...")    # → CognitiveProfile

    from cognitive_module import profile_to_budget_score, score_to_tier
    budget  = profile_to_budget_score(profile)   # → int (0-100)
    tier    = score_to_tier(budget)               # → "Tier 0" ... "Tier 4"

Architecture:
    ┌─────────────────────────────────────────────────────┐
    │                  cognitive_module                     │
    │                                                       │
    │  models.py        — CognitiveProfile, TaskType        │
    │  config.py        — CognitiveConfig (all params)      │
    │  feature_extractor— 42 numerical features             │
    │  rule_scorer.py   — heuristic scorer (always ready)   │
    │  ml_scorer.py     — DistilBERT scorer (scaffold)      │
    │  scorer.py        — BaseScorer ABC + factory          │
    │  routing.py       — tier assignment, budget score     │
    │  training_data.py — label data for fine-tuning        │
    └─────────────────────────────────────────────────────┘
"""

__version__ = "1.0.0"

# ── Core models ──────────────────────────────────────────────────────────────
from .models import CognitiveProfile, TaskType, TASK_TYPE_META

# ── Configuration ────────────────────────────────────────────────────────────
from .config import CognitiveConfig, DEFAULT_CONFIG

# ── Scorer factory (main entry point) ────────────────────────────────────────
from .scorer import create_scorer, BaseScorer

# ── Routing utilities ────────────────────────────────────────────────────────
from .routing import (
    profile_to_budget_score,
    score_to_tier,
    generate_routing_reason,
)

# ── Feature extractor (for advanced usage) ───────────────────────────────────
from .feature_extractor import FeatureExtractor, FEATURE_NAMES

__all__ = [
    # Models
    "CognitiveProfile",
    "TaskType",
    "TASK_TYPE_META",
    # Config
    "CognitiveConfig",
    "DEFAULT_CONFIG",
    # Scorer
    "create_scorer",
    "BaseScorer",
    # Routing
    "profile_to_budget_score",
    "score_to_tier",
    "generate_routing_reason",
    # Features
    "FeatureExtractor",
    "FEATURE_NAMES",
]
