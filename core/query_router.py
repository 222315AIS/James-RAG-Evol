"""
PROJECT JAMES — Query Router (Phase 7, Hybrid)

하이브리드 라우팅:
  1. 명확한 패턴 → 즉시 분류 (LLM 없음, 0ms)
  2. 불명확한 경우 → LLM 의도 분류기 위임

확장 구조:
  새 모드 추가 = intent_classifier.py의 프롬프트만 수정
  키워드 리스트 유지 불필요
"""


class QueryRouter:
    """
    하이브리드 Query Router.

    fast_patterns → 즉시 분류
    나머지        → IntentClassifier (LLM)
    """

    def route(self, query: str, user_role: str = "external") -> str:
        """
        Returns: mode 문자열
          chat / retrieval / coding / wiki_edit /
          agent / self_evolve / app_dev
        """
        from core.intent_classifier import classify_intent
        mode, method = classify_intent(query, user_role=user_role)
        return mode
