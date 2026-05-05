"""
PROJECT JAMES - LLM Router (Phase 6)

GPU 업그레이드 후 실제 Multi-LLM 분기 구현.

분기 기준:
  task_type == "coding"  → qwen2.5-coder:32b  (QwenCoderClient)
  task_type == "vision"  → llava:13b           (Phase 6 후반)
  그 외                  → gemma4:e4b          (기본)

VRAM 주의:
  동시에 2개 모델 로드 시 VRAM 초과 가능
  한 번에 하나씩만 (lazy init + 교체 방식)
"""

import json
from datetime import datetime
from typing import Optional, Dict

from llm.base import BaseLLM

SYSTEM_LOG_PATH = "james_system_log.jsonl"

# ─── lazy init 캐시 ─────────────────────────────────────────

_llm_instances: Dict[str, BaseLLM] = {}


def _log(step: str, detail: str):
    try:
        entry = {"time": datetime.now().isoformat(), "level": "INFO",
                 "step": f"llm_router.{step}", "detail": detail[:200]}
        with open(SYSTEM_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _get_llm(model_key: str) -> Optional[BaseLLM]:
    """lazy init — 요청 시점에만 로드 (VRAM 절약)"""
    if model_key in _llm_instances:
        return _llm_instances[model_key]

    try:
        if model_key == "coding":
            from llm.providers.deepseek_client import QwenCoderClient
            inst = QwenCoderClient()   # qwen2.5-coder:32b
        elif model_key == "vision":
            from llm.providers.llava_client import LlavaClient
            inst = LlavaClient()       # llava:13b (Phase 6 후반)
        else:
            from llm.providers.ollama_client import OllamaClient
            inst = OllamaClient()      # gemma4:e4b 기본

        _llm_instances[model_key] = inst
        _log("load", f"모델 로드: {model_key} ({inst.name})")
        return inst

    except ImportError as e:
        _log("load_fail", f"{model_key}: {e}")
        return None


# ─── 공개 API ────────────────────────────────────────────────

def get_llm(task_type: str = "general") -> BaseLLM:
    """
    task_type 기반 LLM 선택.
    실패 시 기본 모델로 fallback.
    """
    model_key = {"coding": "coding", "vision": "vision"}.get(task_type, "default")

    llm = _get_llm(model_key)
    if llm is None or not llm.is_available():
        _log("fallback", f"task={task_type} → default fallback")
        llm = _get_llm("default")

    return llm


def classify_task(query: str) -> str:
    """
    쿼리 기반 task_type 자동 분류.
    LLM 호출 없이 키워드 기반으로만 판단.
    """
    q = query.lower()

    coding_keywords = [
        "코드", "함수", "클래스", "버그", "디버그", "리팩토링", "구현",
        "python", "javascript", "java", "def ", "class ", "import ",
        "algorithm", "code", "function", "error", "traceback", "syntax",
    ]
    if any(kw in q for kw in coding_keywords):
        return "coding"

    vision_keywords = ["이미지", "사진", "그림", "image", "photo", "picture", "vision"]
    if any(kw in q for kw in vision_keywords):
        return "vision"

    return "general"


def route(query: str, task_type: Optional[str] = None) -> BaseLLM:
    """
    쿼리 또는 명시적 task_type으로 LLM 라우팅.

    Args:
        query:     사용자 쿼리 (task_type 미지정 시 자동 분류)
        task_type: 명시적 지정

    Returns:
        선택된 LLM 인스턴스
    """
    if task_type is None:
        task_type = classify_task(query)

    llm = get_llm(task_type)
    _log("route", f"task={task_type} → {llm.name if llm else 'None'}")
    print(f"[LLM_ROUTER] task={task_type} → {llm.name if llm else 'fallback'}")
    return llm


def list_available() -> Dict[str, bool]:
    """현재 사용 가능한 LLM 목록"""
    result = {}
    for key in ["default", "coding", "vision"]:
        llm = _get_llm(key)
        result[key] = llm.is_available() if llm else False
    return result


# ─── 자가 테스트 ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=== LLM Router 자가 테스트 ===\n")

    cases = [
        ("파이썬 함수 작성해줘", "coding"),
        ("코드 버그 찾아줘",     "coding"),
        ("경제학이란 무엇인가?", "general"),
        ("이 이미지를 분석해줘", "vision"),
        ("서울대학교 위치는?",   "general"),
    ]
    passed = 0
    for query, expected in cases:
        result = classify_task(query)
        ok = result == expected
        passed += int(ok)
        print(f"  {'✅' if ok else '❌'} '{query}' → {result} (기대={expected})")

    print(f"\n  결과: {passed}/{len(cases)} PASS")
