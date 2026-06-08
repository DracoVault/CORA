"""
cognitive_module.models
───────────────────────
Core data models, enums, and metadata for cognitive analysis.
Shared across all scorers (rule-based and ML).
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


# ────────────────────────────────────────────────────────────────────────────────
#  Task Types
# ────────────────────────────────────────────────────────────────────────────────

class TaskType(str, Enum):
    """Classification of prompt intent / task category."""
    FACTUAL        = "factual"
    ANALYTICAL     = "analytical"
    CODE           = "code"
    DEBUGGING      = "debugging"
    CREATIVE       = "creative"
    CONVERSATIONAL = "conversational"
    MATHEMATICAL   = "mathematical"
    MULTI_STEP     = "multi_step"


TASK_TYPE_META: Dict[TaskType, Dict] = {
    TaskType.FACTUAL:        {"icon": "", "label": "Factual",        "boost": 0},
    TaskType.ANALYTICAL:     {"icon": "", "label": "Analytical",     "boost": 10},
    TaskType.CODE:           {"icon": "", "label": "Code",           "boost": 15},
    TaskType.DEBUGGING:      {"icon": "", "label": "Debugging",      "boost": 20},
    TaskType.CREATIVE:       {"icon": "", "label": "Creative",       "boost": 5},
    TaskType.CONVERSATIONAL: {"icon": "", "label": "Conversational", "boost": -5},
    TaskType.MATHEMATICAL:   {"icon": "", "label": "Mathematical",   "boost": 12},
    TaskType.MULTI_STEP:     {"icon": "", "label": "Multi-Step",     "boost": 15},
}


# ────────────────────────────────────────────────────────────────────────────────
#  Cognitive Profile
# ────────────────────────────────────────────────────────────────────────────────

@dataclass
class CognitiveProfile:
    """
    Result of cognitive analysis — 6 dimension scores, task type,
    confidence, and the raw signals that contributed to scoring.
    """
    # ── 6 Cognitive Dimensions (each 0–100) ──
    reasoning_depth: int        = 0
    domain_specificity: int     = 0
    code_complexity: int        = 0
    creative_demand: int        = 0
    precision_required: int     = 0
    structural_complexity: int  = 0

    # ── Classification ──
    task_type: TaskType   = TaskType.CONVERSATIONAL
    confidence: float     = 0.0   # 0.0 – 1.0

    # ── Explainability ──
    signals: List[str]         = field(default_factory=list)
    scorer_used: str           = "rule"   # "rule" or "ml"

    def to_dict(self) -> dict:
        """Serialise to a plain dict (JSON-safe)."""
        d = asdict(self)
        d["task_type"] = self.task_type.value
        return d

    def dimension_dict(self) -> Dict[str, int]:
        """Return just the 6 dimension scores as a dict."""
        return {
            "reasoning_depth":       self.reasoning_depth,
            "domain_specificity":    self.domain_specificity,
            "code_complexity":       self.code_complexity,
            "creative_demand":       self.creative_demand,
            "precision_required":    self.precision_required,
            "structural_complexity": self.structural_complexity,
        }

    def dimension_vector(self) -> List[int]:
        """Return the 6 dimension scores as a flat list (fixed order)."""
        return [
            self.reasoning_depth,
            self.domain_specificity,
            self.code_complexity,
            self.creative_demand,
            self.precision_required,
            self.structural_complexity,
        ]

    @property
    def dominant_dimension(self) -> str:
        """Name of the highest-scoring dimension."""
        dims = self.dimension_dict()
        return max(dims, key=dims.get)  # type: ignore[arg-type]
