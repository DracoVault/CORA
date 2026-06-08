"""
cognitive_module.llm_scorer
───────────────────────────
Uses an LLM (e.g., GPT-OSS or LLaMA-3 via NVIDIA API) to act as a 
cognition-aware prompt complexity classifier. This approach focuses on
true reasoning demand rather than superficial features like token length.
"""

from __future__ import annotations

import os
import json
import logging
from typing import Optional

from openai import OpenAI

from .models import CognitiveProfile, TaskType
from .config import CognitiveConfig, DEFAULT_CONFIG

logger = logging.getLogger("cora.llm_scorer")

# Use a fast, reasoning-capable model
MODEL_ID = "meta/llama3-70b-instruct"
API_KEY_ENV = "NVIDIA_API_KEY"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

def get_api_key() -> str:
    # Use standard NVIDIA API key, fallback to the OSS one if needed
    return os.getenv(API_KEY_ENV, os.getenv("NVIDIA_GPT_OSS_API_KEY", "")).strip()

class LLMBasedScorer:
    """
    LLM-based cognitive scorer.
    Passes the prompt to an LLM evaluator to extract true cognitive demand,
    ignoring superficial features like length or vocabulary.
    """

    def __init__(self, config: CognitiveConfig | None = None):
        self.config = config or DEFAULT_CONFIG
        self._fallback = None  # Lazy load
        
    def _get_fallback(self):
        if self._fallback is None:
            from .rule_scorer import RuleBasedScorer
            self._fallback = RuleBasedScorer(config=self.config)
        return self._fallback

    def score(self, prompt: str) -> CognitiveProfile:
        """Analyse a prompt using an LLM and return a CognitiveProfile."""
        key = get_api_key()
        if not key:
            logger.warning("No NVIDIA API key found for LLM Scorer. Falling back to rules.")
            return self._get_fallback().score(prompt)

        system_instruction = """You are a cognition-aware prompt complexity classifier used in an LLM orchestration system.
Your task is to estimate the true cognitive demand of the user's prompt, rather than relying on surface-level characteristics like token length or vocabulary.

Rules:
1. Extract and isolate the actual task intent from the prompt. Distinguish between contextual text and actionable instructions.
2. Prioritize the final user intent over preceding descriptive or narrative content.
3. Identify the number of reasoning steps required:
   - single-step response
   - multi-step reasoning
   - constraint-based reasoning
   - system design or analytical depth
4. Detect patterns:
   - "explain", "summarize", "compare" -> moderate complexity
   - "design", "prove", "analyze deeply" -> high complexity
   - greetings or direct questions -> low complexity
5. Introduce a context-weight reduction mechanism:
   - If a large portion of the prompt is descriptive but not required for reasoning, reduce its influence on complexity scoring.
6. Assign a cognitive score (0-100) based on reasoning depth, logical dependency, number of steps, and abstraction level.
7. Map the score to tiers:
   - 0-20 -> Tier 0
   - 21-40 -> Tier 1
   - 41-60 -> Tier 2
   - 61-80 -> Tier 3
   - 81-100 -> Tier 4
8. Overriding Rule: If the final instruction is trivial (e.g., greeting, simple factual response), override the score to a low tier regardless of prompt length.

Return ONLY valid JSON matching this schema:
{
  "task_intent": "extracted intent",
  "reasoning_steps": "description of steps",
  "context_weight": "reduced/normal/heavy",
  "cognitive_score": 0,
  "assigned_tier": "T0-T4",
  "justification": "reasoning for this classification"
}"""

        client = OpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=key,
            timeout=10.0
        )

        try:
            completion = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            raw_response = completion.choices[0].message.content
            data = json.loads(raw_response)
            
            # Map back to CognitiveProfile
            score = data.get("cognitive_score", 10)
            
            # Infer TaskType from intent or steps
            intent_lower = data.get("task_intent", "").lower()
            if "design" in intent_lower or "code" in intent_lower or "implement" in intent_lower:
                task_type = TaskType.CODE
            elif "debug" in intent_lower or "fix" in intent_lower:
                task_type = TaskType.DEBUGGING
            elif "math" in intent_lower or "calculate" in intent_lower:
                task_type = TaskType.MATHEMATICAL
            elif "creative" in intent_lower or "story" in intent_lower or "poem" in intent_lower:
                task_type = TaskType.CREATIVE
            elif "analyze" in intent_lower or "compare" in intent_lower:
                task_type = TaskType.ANALYTICAL
            elif "summarize" in intent_lower or "factual" in intent_lower or "what is" in intent_lower:
                task_type = TaskType.FACTUAL
            else:
                if score > 60:
                    task_type = TaskType.MULTI_STEP
                else:
                    task_type = TaskType.CONVERSATIONAL
            
            # Distribute the overall score to the 6 dimensions
            return CognitiveProfile(
                reasoning_depth=score,
                domain_specificity=min(100, int(score * 0.8)),
                code_complexity=score if task_type in (TaskType.CODE, TaskType.DEBUGGING) else 10,
                creative_demand=score if task_type == TaskType.CREATIVE else 10,
                precision_required=score if task_type == TaskType.MATHEMATICAL else int(score * 0.6),
                structural_complexity=score if task_type == TaskType.MULTI_STEP else int(score * 0.7),
                task_type=task_type,
                confidence=0.9,
                signals=[f"llm_intent: {data.get('task_intent', '')}", f"llm_justification: {data.get('justification', '')}"],
                scorer_used="llm"
            )
            
        except Exception as e:
            logger.error(f"LLM Scorer inference failed: {e}")
            return self._get_fallback().score(prompt)
