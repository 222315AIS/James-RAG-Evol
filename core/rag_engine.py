"""
PROJECT JAMES - RAG Engine (DEPRECATED)

⚠️  이 파일은 더 이상 메인 엔진이 아닙니다.
    메인 엔진: core/graph_rag_engine.py

이전 완료 목록:
  hybrid_search       → graph_rag_engine.RAGEngine.hybrid_search()
  calculate_confidence→ graph_rag_engine.RAGEngine.calculate_confidence()
  normalize_bm25      → graph_rag_engine.RAGEngine._normalize_bm25()
  extract_names       → utils/tokenizer.extract_names()
  split_chunks        → utils/tokenizer.split_chunks()
  vector_search       → core/vector_store.VectorStore.search()
  save_to_chroma      → core/vector_store.VectorStore.add_documents_with_meta()
  _sanitize_for_ingest→ core/security.SecurityManager.sanitize_for_vector_ingest()
  generate_answer     → graph_rag_engine.RAGEngine.generate_answer()
  process_query       → graph_rag_engine.RAGEngine.query()

외부에서 RAGEngine을 import하는 코드가 있다면:
  ❌ from core.rag_engine import RAGEngine
  ✅ from core.graph_rag_engine import RAGEngine
"""


class RAGEngine:
    """
    DEPRECATED — graph_rag_engine.RAGEngine을 사용하세요.
    하위 호환성 유지를 위해 임시 래퍼로만 남김.
    """

    def __init__(self, *args, **kwargs):
        import warnings
        warnings.warn(
            "RAGEngine (rag_engine.py) is deprecated. "
            "Use core.graph_rag_engine.RAGEngine instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from core.graph_rag_engine import RAGEngine as _GraphRAGEngine
        self._engine = _GraphRAGEngine(*args, **kwargs)
        # 주요 속성 위임
        self.vector_store   = self._engine.vector_store
        self.wiki_generator = self._engine.wiki_generator
        self.llm            = self._engine.llm

    def process_query(self, question: str, user_role: str = "external") -> dict:
        """하위 호환 — graph_rag_engine.query()로 위임"""
        return self._engine.query(user_query=question, user_role=user_role)

    def query(self, *args, **kwargs):
        return self._engine.query(*args, **kwargs)

    def hybrid_search(self, question: str, top_k: int = 8) -> list:
        return self._engine.hybrid_search(question, top_k)

    def generate_metadata(self, text: str) -> dict:
        from utils.metadata import MetadataGenerator
        return MetadataGenerator().generate_metadata(text)

    def save_to_wiki(self, filename: str, content: str, meta: dict) -> str:
        """하위 호환 — vector_store + wiki_generator로 위임"""
        from utils.tokenizer import split_chunks
        chunks = split_chunks(content)
        self.vector_store.add_documents_with_meta(
            texts=chunks, source=filename,
            metadata={
                "sensitivity": meta.get("sensitivity", "internal"),
                "owner":       meta.get("owner", "system"),
                "category":    meta.get("category", "기타"),
            }
        )
        return filename
