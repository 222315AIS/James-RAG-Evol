"""
PROJECT JAMES - Ollama Client (Phase 5.5)

기존 GemmaClient 래핑. 새 로직 없음.
Multi-LLM 라우터는 Phase 6 이후.
"""

from llm.base import BaseLLM
from typing import List, Dict


class OllamaClient(BaseLLM):
    name = "ollama"

    def generate(self, messages: List[Dict], **kwargs) -> str:
        """messages → 단일 prompt 변환 후 GemmaClient 호출."""
        from core.gemma_client import GemmaClient
        prompt  = "\n".join(m.get("content","") for m in messages if m.get("content"))
        timeout = kwargs.get("timeout", 120)
        return GemmaClient().call_gemma(prompt, timeout=timeout, use_cache=True)

    def is_available(self) -> bool:
        try:
            import requests
            requests.get("http://127.0.0.1:11434", timeout=2)
            return True
        except Exception:
            return False
