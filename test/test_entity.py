from core.graph_rag_engine import RAGEngine

engine = RAGEngine()

result = engine.extract_entities("김철수는 무엇을 공부하는가?", [])

print(result)