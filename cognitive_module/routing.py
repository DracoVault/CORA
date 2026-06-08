"""
cognitive_module.routing
────────────────────────
Tier assignment, budget score aggregation, and routing reason generation.

These are routing-layer concerns (not scoring concerns), so they live
separately from the scorers.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .models import CognitiveProfile, TaskType, TASK_TYPE_META
from .config import CognitiveConfig, DEFAULT_CONFIG


# ────────────────────────────────────────────────────────────────────────────────
#  Budget Score Aggregation
# ────────────────────────────────────────────────────────────────────────────────

def profile_to_budget_score(
    profile: CognitiveProfile,
    config: CognitiveConfig | None = None,
) -> int:
    """
    Convert a CognitiveProfile into a single 0–100 budget score.
    
    Uses a hybrid approach:
      - 50% weighted average across all 6 dimensions
      - 50% average of the top-2 highest dimensions
    
    This ensures a prompt that's very complex on 2-3 axes
    isn't dragged to Tier 0 by zeros on the other dimensions.
    """
    cfg = config or DEFAULT_CONFIG
    weights = cfg.dimension_weights

    dims = [
        profile.reasoning_depth,
        profile.code_complexity,
        profile.domain_specificity,
        profile.structural_complexity,
        profile.creative_demand,
        profile.precision_required,
    ]

    # Weighted average (original formula)
    weighted = (
        profile.reasoning_depth       * weights.get("reasoning_depth", 0.25)
        + profile.code_complexity     * weights.get("code_complexity", 0.25)
        + profile.domain_specificity  * weights.get("domain_specificity", 0.15)
        + profile.structural_complexity * weights.get("structural_complexity", 0.15)
        + profile.creative_demand     * weights.get("creative_demand", 0.10)
        + profile.precision_required  * weights.get("precision_required", 0.10)
    )

    # Peak score: average of top-2 dimensions
    sorted_dims = sorted(dims, reverse=True)
    peak = (sorted_dims[0] + sorted_dims[1]) / 2

    # Hybrid: blend weighted average with peak signal
    hybrid = weighted * 0.5 + peak * 0.5

    # Task-type boost (soft override)
    boost = TASK_TYPE_META[profile.task_type]["boost"]
    final = hybrid + boost
    
    # Scale scores up to fill the user's tier boundaries 
    # (Tier 4 starts at 89, but original rule scorer maxed around 85 for most prompts)
    if final > 10:
        final = final * 1.25

    return min(max(int(round(final)), 1), 100)


# ────────────────────────────────────────────────────────────────────────────────
#  Tier Assignment
# ────────────────────────────────────────────────────────────────────────────────

def score_to_tier(
    score: int,
    config: CognitiveConfig | None = None,
) -> str:
    """Map a budget score to a model tier using config boundaries."""
    cfg = config or DEFAULT_CONFIG

    for max_score, tier_name in cfg.tier_boundaries:
        if score <= max_score:
            return tier_name

    # Fallback (should not happen if config is correct)
    return cfg.tier_boundaries[-1][1]


# ────────────────────────────────────────────────────────────────────────────────
#  Routing Reason Generator
# ────────────────────────────────────────────────────────────────────────────────

def generate_routing_reason(
    profile: CognitiveProfile,
    tier: str,
    model: str,
) -> str:
    """
    Generate a human-readable explanation of why a prompt was
    routed to a particular tier and model.
    """
    meta = TASK_TYPE_META[profile.task_type]
    task_label = f"{meta['icon']} {meta['label']}"

    # Find the dominant dimension
    dims = {
        "Reasoning Depth":       profile.reasoning_depth,
        "Domain Specificity":    profile.domain_specificity,
        "Code Complexity":       profile.code_complexity,
        "Creative Demand":       profile.creative_demand,
        "Precision Required":    profile.precision_required,
        "Structural Complexity": profile.structural_complexity,
    }
    dominant = max(dims, key=dims.get)  # type: ignore[arg-type]
    dominant_score = dims[dominant]

    # Build explanation parts
    parts = [f"Detected task type: {task_label}"]

    if dominant_score >= 30:
        parts.append(f"Primary signal: {dominant} ({dominant_score}/100)")

    # Secondary dimensions
    secondary = [
        f"{k} ({v})"
        for k, v in sorted(dims.items(), key=lambda x: x[1], reverse=True)
        if k != dominant and v >= 20
    ]
    if secondary:
        parts.append(f"Contributing factors: {', '.join(secondary[:3])}")

    # Confidence
    if profile.confidence >= 0.8:
        parts.append(f"Classification confidence: High ({int(profile.confidence * 100)}%)")
    elif profile.confidence >= 0.6:
        parts.append(f"Classification confidence: Medium ({int(profile.confidence * 100)}%)")
    else:
        parts.append(f"Classification confidence: Low ({int(profile.confidence * 100)}%)")

    # Scorer used
    parts.append(f"Scorer: {profile.scorer_used}")

    # Task-type boost
    boost = meta["boost"]
    if boost != 0:
        direction = "↑" if boost > 0 else "↓"
        parts.append(f"Task-type adjustment: {direction}{abs(boost)} pts")

    parts.append(f"Routed to {tier} → {model}")

    return " · ".join(parts)
