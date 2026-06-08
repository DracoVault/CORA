"""
cognitive_module.ml_scorer
──────────────────────────
DistilBERT-based cognitive scorer scaffold.

Architecture:
  DistilBERT encoder → [CLS] hidden state (768-d)
                        ↓
       ┌────────────────┼────────────────────┐
       │ (optional) concat 42 hand-crafted   │
       │ features from FeatureExtractor      │
       └────────────────┼────────────────────┘
                        ↓
            ┌───────────┴───────────┐
            │  Regression Head      │  → 6 dimension scores (0–100)
            │  Classification Head  │  → 8-class TaskType
            └───────────────────────┘

This file scaffolds the full inference pipeline.
Training requires a fine-tuned checkpoint — see training_data.py
for generating the labelled dataset.

IMPORTANT: This module gracefully handles missing `transformers`
and `torch` libraries. If they're not installed, it falls back
to the rule-based scorer automatically.
"""

from __future__ import annotations

import os
import logging
from typing import Optional, Tuple, List

from .models import CognitiveProfile, TaskType
from .config import CognitiveConfig, DEFAULT_CONFIG
from .feature_extractor import FeatureExtractor

logger = logging.getLogger("cora.ml_scorer")

# ── Graceful import of ML dependencies ──────────────────────────────────────
_ML_AVAILABLE = False
try:
    import torch
    import torch.nn as nn
    from transformers import DistilBertTokenizer, DistilBertModel
    _ML_AVAILABLE = True
except ImportError:
    torch = None  # type: ignore
    nn = None     # type: ignore
    logger.info(
        "torch/transformers not installed — ML scorer unavailable, "
        "will fall back to rule-based scorer."
    )


# ── Task type labels (must match TaskType enum order) ───────────────────────
_TASK_LABELS: List[TaskType] = [
    TaskType.FACTUAL,
    TaskType.ANALYTICAL,
    TaskType.CODE,
    TaskType.DEBUGGING,
    TaskType.CREATIVE,
    TaskType.CONVERSATIONAL,
    TaskType.MATHEMATICAL,
    TaskType.MULTI_STEP,
]


# ════════════════════════════════════════════════════════════════════════════════
#  MODEL DEFINITION
# ════════════════════════════════════════════════════════════════════════════════

if _ML_AVAILABLE:

    class CORADistilBertModel(nn.Module):
        """
        Custom DistilBERT model for CORA cognitive analysis.

        Inputs:
            - input_ids, attention_mask  (from tokenizer)
            - hand_features             (42 features from FeatureExtractor)

        Outputs:
            - dimension_scores: Tensor[batch, 6]  (0–100 per dimension)
            - task_logits:      Tensor[batch, 8]  (8-class task type)
            - confidence:       Tensor[batch, 1]  (0–1 confidence)
        """

        def __init__(
            self,
            model_name: str = "distilbert-base-uncased",
            num_dimensions: int = 6,
            num_task_types: int = 8,
            num_hand_features: int = 42,
            use_hand_features: bool = True,
        ):
            super().__init__()
            self.use_hand_features = use_hand_features

            # DistilBERT backbone
            self.distilbert = DistilBertModel.from_pretrained(model_name)
            hidden_size = self.distilbert.config.hidden_size  # 768

            # Feature fusion dimension
            fusion_size = hidden_size + (num_hand_features if use_hand_features else 0)

            # Shared projection layer
            self.projection = nn.Sequential(
                nn.Linear(fusion_size, 512),
                nn.LayerNorm(512),
                nn.GELU(),
                nn.Dropout(0.1),
                nn.Linear(512, 256),
                nn.LayerNorm(256),
                nn.GELU(),
                nn.Dropout(0.1),
            )

            # Regression head → 6 dimension scores
            self.dimension_head = nn.Sequential(
                nn.Linear(256, 128),
                nn.GELU(),
                nn.Linear(128, num_dimensions),
                nn.Sigmoid(),  # output 0–1, multiply by 100 later
            )

            # Classification head → 8 task types
            self.task_head = nn.Sequential(
                nn.Linear(256, 128),
                nn.GELU(),
                nn.Linear(128, num_task_types),
            )

            # Confidence head → 1 scalar
            self.confidence_head = nn.Sequential(
                nn.Linear(256, 64),
                nn.GELU(),
                nn.Linear(64, 1),
                nn.Sigmoid(),
            )

        def forward(
            self,
            input_ids: torch.Tensor,
            attention_mask: torch.Tensor,
            hand_features: Optional[torch.Tensor] = None,
        ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
            # Encode with DistilBERT
            outputs = self.distilbert(
                input_ids=input_ids,
                attention_mask=attention_mask,
            )
            cls_embedding = outputs.last_hidden_state[:, 0, :]  # [CLS] token

            # Optionally concat hand-crafted features
            if self.use_hand_features and hand_features is not None:
                fused = torch.cat([cls_embedding, hand_features], dim=-1)
            else:
                fused = cls_embedding

            # Shared projection
            projected = self.projection(fused)

            # Heads
            dim_scores = self.dimension_head(projected) * 100  # scale to 0–100
            task_logits = self.task_head(projected)
            confidence = self.confidence_head(projected)

            return dim_scores, task_logits, confidence


# ════════════════════════════════════════════════════════════════════════════════
#  SCORER CLASS
# ════════════════════════════════════════════════════════════════════════════════

class DistilBERTScorer:
    """
    ML-based cognitive scorer using a fine-tuned DistilBERT model.

    Falls back to rule-based scoring if:
      - torch/transformers are not installed
      - no model checkpoint is found at config.ml_model_path
      - model confidence is below threshold
    """

    def __init__(self, config: CognitiveConfig | None = None):
        self.config = config or DEFAULT_CONFIG
        self._extractor = FeatureExtractor()
        self._model: Optional[object] = None
        self._tokenizer = None
        self._ready = False

        # Lazy-import the rule scorer for fallback
        from .rule_scorer import RuleBasedScorer
        self._fallback = RuleBasedScorer(config=self.config)

        self._try_load_model()

    def _try_load_model(self) -> None:
        """Attempt to load the fine-tuned model. Fail silently if not available."""
        if not _ML_AVAILABLE:
            logger.warning("ML libraries not available — using rule-based fallback.")
            return

        model_path = self.config.ml_model_path
        if not os.path.exists(model_path):
            logger.info(
                f"No model checkpoint at '{model_path}' — using rule-based fallback. "
                f"Train a model with training_data.py and save to this path."
            )
            return

        try:
            self._tokenizer = DistilBertTokenizer.from_pretrained(model_path)
            self._model = CORADistilBertModel.from_pretrained_checkpoint(model_path)

            # Move to device
            device = self.config.ml_device
            if device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model.to(device)
            self._model.eval()
            self._ready = True
            logger.info(f"Loaded DistilBERT model from '{model_path}' on {device}")
        except Exception as e:
            logger.error(f"Failed to load model: {e} — using rule-based fallback.")
            self._ready = False

    @property
    def is_ml_ready(self) -> bool:
        """Whether the ML model is loaded and ready for inference."""
        return self._ready

    def score(self, prompt: str) -> CognitiveProfile:
        """
        Score a prompt using DistilBERT inference.
        Falls back to rule-based scorer if ML is unavailable or low-confidence.
        """
        if not self._ready:
            return self._fallback.score(prompt)

        try:
            profile = self._ml_inference(prompt)

            # Confidence check — fall back if model is unsure
            if profile.confidence < self.config.ml_confidence_threshold:
                logger.debug(
                    f"ML confidence {profile.confidence:.2f} below threshold "
                    f"{self.config.ml_confidence_threshold} — using rule fallback."
                )
                return self._fallback.score(prompt)

            return profile

        except Exception as e:
            logger.error(f"ML inference failed: {e} — using rule-based fallback.")
            return self._fallback.score(prompt)

    def _ml_inference(self, prompt: str) -> CognitiveProfile:
        """Run the actual DistilBERT inference."""
        assert self._model is not None and self._tokenizer is not None

        device = self.config.ml_device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        # Tokenize
        inputs = self._tokenizer(
            prompt,
            max_length=self.config.ml_max_seq_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        input_ids = inputs["input_ids"].to(device)
        attention_mask = inputs["attention_mask"].to(device)

        # Extract hand-crafted features
        feat_vector = self._extractor.extract_vector(prompt)
        hand_features = torch.tensor([feat_vector], dtype=torch.float32).to(device)

        # Inference
        with torch.no_grad():
            dim_scores, task_logits, confidence = self._model(
                input_ids, attention_mask, hand_features
            )

        # Parse outputs
        dims = dim_scores[0].cpu().tolist()
        task_idx = task_logits[0].argmax().item()
        conf = confidence[0].item()

        profile = CognitiveProfile(
            reasoning_depth=int(round(dims[0])),
            domain_specificity=int(round(dims[1])),
            code_complexity=int(round(dims[2])),
            creative_demand=int(round(dims[3])),
            precision_required=int(round(dims[4])),
            structural_complexity=int(round(dims[5])),
            task_type=_TASK_LABELS[task_idx],
            confidence=round(conf, 2),
            signals=["ml_distilbert_inference"],
            scorer_used="ml",
        )

        return profile

    @property
    def extractor(self) -> FeatureExtractor:
        """Expose the feature extractor."""
        return self._extractor
