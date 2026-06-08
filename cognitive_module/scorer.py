"""
cognitive_module.scorer
───────────────────────
Abstract base class + factory for swapping between rule-based
and ML-based cognitive scorers via the Strategy pattern.

Usage:
    from cognitive_module import create_scorer

    scorer = create_scorer("rule")      # heuristic scorer
    scorer = create_scorer("ml")        # DistilBERT (fallback to rule)
    scorer = create_scorer()            # auto from CORA_SCORER_MODE env var

    profile = scorer.score("Explain how transformers work")
"""

from __future__ import annotations

import os
import logging
from abc import ABC, abstractmethod
from typing import Optional

from .models import CognitiveProfile
from .config import CognitiveConfig, DEFAULT_CONFIG

logger = logging.getLogger("cora.scorer")


# ────────────────────────────────────────────────────────────────────────────────
#  Abstract Base
# ────────────────────────────────────────────────────────────────────────────────

class BaseScorer(ABC):
    """
    Abstract interface for cognitive scorers.

    All scorers (rule-based, ML, hybrid) implement this interface,
    so callers don't need to know which engine is running underneath.
    """

    @abstractmethod
    def score(self, prompt: str) -> CognitiveProfile:
        """
        Analyse a prompt and return a CognitiveProfile with:
          - 6 dimension scores (0–100 each)
          - Detected TaskType
          - Confidence (0–1)
          - Explainability signals
        """
        ...


# ────────────────────────────────────────────────────────────────────────────────
#  Factory
# ────────────────────────────────────────────────────────────────────────────────

def create_scorer(
    mode: Optional[str] = None,
    config: Optional[CognitiveConfig] = None,
) -> BaseScorer:
    """
    Create a cognitive scorer instance.

    Args:
        mode:   "rule", "ml", "nemo", or None (auto-detect from env CORA_SCORER_MODE)
        config: Optional CognitiveConfig override

    Returns:
        A scorer implementing BaseScorer.

    Behaviour:
        - mode="rule"  → RuleBasedScorer (always available)
        - mode="ml"    → DistilBERTScorer (falls back to rule if unavailable)
        - mode="nemo"  → NeMoScorer (falls back to rule if unavailable)
        - mode="llm"   → LLMBasedScorer (uses LLM API, falls back to rule)
        - mode=None    → reads os.environ["CORA_SCORER_MODE"], defaults to "rule"
    """
    cfg = config or DEFAULT_CONFIG

    if mode is None:
        mode = os.environ.get("CORA_SCORER_MODE", "rule").lower()

    if mode == "nemo":
        from .nemo_scorer import NeMoScorer

        scorer = NeMoScorer(config=cfg)
        logger.info(
            f"NeMo scorer created. "
            f"Will {'use DeBERTa' if getattr(scorer, '_ready', False) else 'fall back to rules'}."
        )
        return _ScorerAdapter(scorer)
    elif mode == "ml":
        from .ml_scorer import DistilBERTScorer

        scorer = DistilBERTScorer(config=cfg)
        logger.info(
            f"ML scorer created (ready={scorer.is_ml_ready}). "
            f"Will {'use DistilBERT' if scorer.is_ml_ready else 'fall back to rules'}."
        )
        # Wrap in adapter so it satisfies BaseScorer
        return _ScorerAdapter(scorer)
    elif mode == "llm":
        from .llm_scorer import LLMBasedScorer

        scorer = LLMBasedScorer(config=cfg)
        logger.info("LLM scorer created.")
        return _ScorerAdapter(scorer)
    else:
        from .rule_scorer import RuleBasedScorer

        logger.info("Rule-based scorer created.")
        return _ScorerAdapter(RuleBasedScorer(config=cfg))


class _ScorerAdapter(BaseScorer):
    """
    Thin adapter that wraps concrete scorers so they satisfy BaseScorer ABC.
    (Avoids multiple inheritance complexity in the concrete classes.)
    """

    def __init__(self, inner):
        self._inner = inner

    def score(self, prompt: str) -> CognitiveProfile:
        return self._inner.score(prompt)

    def __getattr__(self, name):
        """Delegate any other attribute access to the inner scorer."""
        return getattr(self._inner, name)
