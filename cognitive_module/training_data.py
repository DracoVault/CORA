"""
cognitive_module.training_data
──────────────────────────────
Generate labelled training data for fine-tuning DistilBERT.

Uses the rule-based scorer to label prompts with:
  - 6 dimension scores
  - task type
  - budget score

Output: CSV or JSON file ready for model training.

Usage:
    from cognitive_module.training_data import TrainingDataGenerator

    gen = TrainingDataGenerator()

    # Label prompts
    gen.add_prompt("Explain quantum entanglement step by step")
    gen.add_prompt("hi")
    gen.add_prompt("Fix this TypeError in my Python code: ...")

    # Export
    gen.to_csv("training_data.csv")
    gen.to_json("training_data.json")

    # Or generate from a file of prompts
    gen.from_file("prompts.txt")
    gen.to_csv("training_data.csv")
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .models import CognitiveProfile
from .config import CognitiveConfig, DEFAULT_CONFIG
from .rule_scorer import RuleBasedScorer
from .routing import profile_to_budget_score
from .feature_extractor import FEATURE_NAMES

logger = logging.getLogger("cora.training_data")


class TrainingDataGenerator:
    """
    Generates labelled training data for DistilBERT fine-tuning.

    Workflow:
    1. Collect prompts (add manually or load from file)
    2. Rule-based scorer labels each prompt
    3. Export to CSV/JSON for PyTorch Dataset consumption
    """

    def __init__(self, config: CognitiveConfig | None = None):
        self.config = config or DEFAULT_CONFIG
        self._scorer = RuleBasedScorer(config=self.config)
        self._records: List[Dict[str, Any]] = []

    def add_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Label a single prompt and store the record.
        Returns the labelled record dict.
        """
        profile = self._scorer.score(prompt)
        features = self._scorer.extractor.extract(prompt)
        budget_score = profile_to_budget_score(profile, self.config)

        record = {
            # Input
            "prompt": prompt,
            "word_count": len(prompt.split()),

            # Labels (regression targets)
            "reasoning_depth":       profile.reasoning_depth,
            "domain_specificity":    profile.domain_specificity,
            "code_complexity":       profile.code_complexity,
            "creative_demand":       profile.creative_demand,
            "precision_required":    profile.precision_required,
            "structural_complexity": profile.structural_complexity,

            # Labels (classification target)
            "task_type": profile.task_type.value,
            "confidence": profile.confidence,

            # Aggregate
            "budget_score": budget_score,

            # Hand-crafted features (for hybrid training)
            **{f"feat_{k}": v for k, v in features.items()},
        }

        self._records.append(record)
        return record

    def add_prompts(self, prompts: List[str]) -> int:
        """Label a batch of prompts. Returns number of records added."""
        count = 0
        for prompt in prompts:
            prompt = prompt.strip()
            if prompt:
                self.add_prompt(prompt)
                count += 1
        return count

    def from_file(self, filepath: str, encoding: str = "utf-8") -> int:
        """
        Load prompts from a text file (one prompt per line).
        Returns number of records added.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {filepath}")

        prompts = path.read_text(encoding=encoding).strip().split("\n")
        return self.add_prompts(prompts)

    def to_csv(self, filepath: str) -> None:
        """Export labelled data to CSV."""
        if not self._records:
            logger.warning("No records to export.")
            return

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = list(self._records[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self._records)

        logger.info(f"Exported {len(self._records)} records to {filepath}")

    def to_json(self, filepath: str, indent: int = 2) -> None:
        """Export labelled data to JSON."""
        if not self._records:
            logger.warning("No records to export.")
            return

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._records, f, indent=indent, ensure_ascii=False)

        logger.info(f"Exported {len(self._records)} records to {filepath}")

    def to_records(self) -> List[Dict[str, Any]]:
        """Return the raw records list (for programmatic use)."""
        return list(self._records)

    @property
    def record_count(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        """Clear all stored records."""
        self._records.clear()

    @staticmethod
    def get_label_columns() -> List[str]:
        """
        Return the column names that serve as training labels.
        Useful for building the PyTorch Dataset.
        """
        return [
            "reasoning_depth",
            "domain_specificity",
            "code_complexity",
            "creative_demand",
            "precision_required",
            "structural_complexity",
            "task_type",
            "budget_score",
        ]

    @staticmethod
    def get_feature_columns() -> List[str]:
        """Return the hand-crafted feature column names (prefixed with feat_)."""
        return [f"feat_{name}" for name in FEATURE_NAMES]
