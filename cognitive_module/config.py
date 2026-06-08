"""
cognitive_module.config
───────────────────────
All tuneable parameters in one place.
Dimension weights, tier boundaries, scorer mode, ML model path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class CognitiveConfig:
    """
    Central configuration for the cognitive module.
    Modify these values to tune scoring behaviour without touching code.
    """

    # ── Dimension Weights (must sum to 1.0) ──────────────────────────────────
    dimension_weights: Dict[str, float] = field(default_factory=lambda: {
        "reasoning_depth":       0.25,
        "code_complexity":       0.25,
        "domain_specificity":    0.15,
        "structural_complexity": 0.15,
        "creative_demand":       0.10,
        "precision_required":    0.10,
    })

    # ── Tier Boundaries ──────────────────────────────────────────────────────
    # Each tuple is (max_score_inclusive, tier_name)
    # Evaluated top-to-bottom; first match wins
    tier_boundaries: List[Tuple[int, str]] = field(default_factory=lambda: [
        (20,  "Tier 0"),
        (45,  "Tier 1"),
        (70,  "Tier 2"),
        (88,  "Tier 3"),
        (100, "Tier 4"),
    ])

    # ── Scorer Mode ──────────────────────────────────────────────────────────
    # "rule"  → heuristic rule-based scoring (always available)
    # "ml"    → DistilBERT inference (requires trained checkpoint)
    # "hybrid"→ ML primary with rule-based fallback features
    scorer_mode: str = "rule"

    # ── ML Model Settings ────────────────────────────────────────────────────
    ml_model_path: str = "models/cora_distilbert"
    ml_tokenizer_name: str = "distilbert-base-uncased"
    ml_max_seq_length: int = 256
    ml_device: str = "cpu"   # "cpu", "cuda", "auto"
    ml_confidence_threshold: float = 0.4  # below this → fall back to rule

    # ── Feature Extractor Settings ───────────────────────────────────────────
    # Max number of signals to retain in CognitiveProfile
    max_signals: int = 30


# ── Default singleton ────────────────────────────────────────────────────────
DEFAULT_CONFIG = CognitiveConfig()
