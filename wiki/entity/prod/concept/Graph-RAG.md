---
entity_id: e_concept_fde936cf
name: Graph-RAG
entity_type: concept
sensitivity: public
source_type: prod
owner: system
created_at: 2026-05-03T16:57:13.012759
generated_by: seed_data
relations:
  - target: 자메스시스템
    target_id: e_concept_d2026ec0
    type: PART_OF
    confidence: 1.0
  - target: 김민준
    target_id: e_person_8720ab91
    type: DEVELOPED_BY
    confidence: 0.9
  - target: 이서연
    target_id: e_person_cb35e3e0
    type: DEVELOPED_BY
    confidence: 0.85
---

# Graph-RAG

## 개요
Graph-Retrieval-Augmented Generation의 약어. 그래프 구조 기반 검색 증강 생성 기법.

## 핵심 구성
1. **Vector Search**: 의미 기반 유사도 검색
2. **Graph Traversal**: 엔티티 관계 그래프 탐색 (DFS)
3. **Hybrid Ranking**: 벡터 + BM25 + 키워드 통합 점수
4. **Context Fusion**: 검색 결과 + 그래프 경로 통합

## 단순 RAG 대비 장점
- 환각(hallucination) 감소
- 추론 경로 명시 (explainability)
- 다단계 추론 가능
- 관계 기반 정밀 검색

## 자메스 시스템에서의 구현
graph_rag_engine.py에 통합 구현됨. DFS 깊이 4, 점수 임계값 0.05 사용.
