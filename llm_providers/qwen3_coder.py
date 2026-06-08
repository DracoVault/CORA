"""
llm_providers.qwen3_coder
─────────────────────────
Tier 4 — Qwen3 Coder 480B-A35B Instruct
Frontier MoE model (480B total, 35B active) for the most complex
multi-step reasoning, code generation, and agentic tasks.

Provider : NVIDIA Integrate API (OpenAI-compatible)
Model ID : qwen/qwen3-coder-480b-a35b-instruct
"""

from __future__ import annotations

import os

from .base import call_nvidia_openai

# ── Configuration ────────────────────────────────────────────────────────────
MODEL_ID = "qwen/qwen3-coder-480b-a35b-instruct"
DISPLAY_NAME = "Qwen3 Coder 480B"
TIER = "Tier 4"
API_KEY_ENV = "NVIDIA_QWEN3_CODER_API_KEY"


def get_api_key() -> str:
    return os.getenv(API_KEY_ENV, "").strip()


async def call(prompt: str, api_key: str | None = None) -> str:
    """Send a prompt to Qwen3 Coder 480B and return the response text."""
    key = api_key or get_api_key()
    if not key:
        raise Exception(f"No API key configured for {DISPLAY_NAME} ({API_KEY_ENV})")
    return await call_nvidia_openai(
        model=MODEL_ID,
        prompt=prompt,
        api_key=key,
        temperature=0.7,
        top_p=0.8,
        max_tokens=4096,
    )
