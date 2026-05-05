"""
PROJECT JAMES - Qwen Coder Client (Phase 6)

코딩 전용 모델 qwen2.5-coder:32b. Ollama 통해 로컬 실행.
기존 GemmaClient 구조 그대로 재활용.
"""

from llm.base import BaseLLM
from typing import List, Dict


class QwenCoderClient(BaseLLM):
    name = "qwen-coder"

    def __init__(self):
        try:
            from config import CODING_MODEL, OLLAMA_API_URL
            self.model   = CODING_MODEL       # qwen2.5-coder:32b
            self.api_url = OLLAMA_API_URL
        except ImportError:
            self.model   = "qwen2.5-coder:32b"
            self.api_url = "http://127.0.0.1:11434/api/generate"

    def generate(self, messages: List[Dict], **kwargs) -> str:
        """코딩 전용 프롬프트 형식으로 변환 후 호출."""
        import requests, re
        try:
            from core.gemma_client import _LLM_OPTIONS
        except ImportError:
            _LLM_OPTIONS = {"num_predict": 700, "temperature": 0, "num_ctx": 4096}

        prompt = "\n".join(
            f"{'User' if m.get('role')=='user' else 'Assistant'}: {m.get('content','')}"
            for m in messages if m.get("content")
        )

        coding_prompt = (
            "You are an expert coding assistant. "
            "Provide clear, correct, and efficient code.\n\n"
            f"{prompt}\n\nCode:"
        )

        timeout = kwargs.get("timeout", 120)

        try:
            options = dict(_LLM_OPTIONS)
            options["temperature"] = 0   # 코딩은 결정론적

            resp = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": coding_prompt,
                      "stream": False, "options": options},
                timeout=timeout,
            )
            resp.raise_for_status()
            output = resp.json().get("response", "").strip()

            # think 블록 제거
            cleaned = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()
            return cleaned if cleaned else output

        except Exception as e:
            print(f"[QWEN_CODER] 오류 → GemmaClient fallback: {e}")
            from core.gemma_client import GemmaClient
            return GemmaClient().call_gemma(coding_prompt, timeout=timeout)

    def is_available(self) -> bool:
        """ollama list API로 모델 설치 여부 확인 (응답 타임아웃 문제 방지)"""
        try:
            import requests
            resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
            if resp.status_code != 200:
                return False
            models = [m.get("name","") for m in resp.json().get("models",[])]
            return any(self.model.split(":")[0] in m for m in models)
        except Exception:
            return False


# 기존 이름 호환
DeepSeekCoderClient = QwenCoderClient
