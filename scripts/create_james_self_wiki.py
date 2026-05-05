"""
PROJECT JAMES — 자메스 자기 인식 Wiki 생성 스크립트
실행: python create_james_self_wiki.py

자메스 자신에 대한 정보를 wiki에 저장합니다.
이후 "자메스의 기능은?", "자메스는 어떤 시스템이야?" 같은
질문에 Graph-RAG가 정확하게 답변할 수 있습니다.
"""

import os
from pathlib import Path
from datetime import datetime

try:
    from config import BASE_DIR, WIKI_DIR
except ImportError:
    BASE_DIR = "."
    WIKI_DIR = "./wiki"

WIKI_PATH = Path(WIKI_DIR) if os.path.isabs(WIKI_DIR) else Path(BASE_DIR) / "wiki"

JAMES_ENTITY_CONTENT = f"""---
entity_id: james_system_001
name: 자메스
aliases:
  - James
  - JAMES
  - 자메스 AI
entity_type: concept
sensitivity: internal
source_type: prod
created_at: {datetime.now().isoformat()}
relations:
  - target: Graph-RAG
    target_id: UNRESOLVED
    target_type: concept
    type: USES
    label: 활용
    confidence: 1.0
  - target: ChromaDB
    target_id: UNRESOLVED
    target_type: concept
    type: USES
    label: 활용
    confidence: 1.0
  - target: Gemma
    target_id: UNRESOLVED
    target_type: concept
    type: USES
    label: 활용
    confidence: 1.0
  - target: 보안
    target_id: UNRESOLVED
    target_type: concept
    type: BELONGS_TO
    label: 속함
    confidence: 1.0
---

# 자메스 (PROJECT JAMES)

자메스(James)는 로컬 환경에서 동작하는 **보안 중심 Graph-RAG 기반 지식 추론 시스템**이다.
단순한 AI 챗봇이 아니라, 보안이 보장된 지식 추론 엔진이다.

## 핵심 철학

- **RAG는 불완전하다**: 단순 Vector 검색은 hallucination을 막지 못한다. 반드시 Graph + Ontology 기반 추론이 필요하다.
- **보안은 기능이 아니라 전제다**: 모든 설계는 공격을 전제로 시작한다. "동작한다"보다 "유출되지 않는다"가 우선이다.
- **Graph 없으면 실패**: Graph가 약하면 그냥 느린 검색 엔진이다.

## 현재 기능 (Phase 7 기준)

### 핵심 기능
1. **Graph-RAG 추론**: Graph + Vector + BM25 Hybrid Search로 정확한 지식 검색
2. **Dynamic DFS 탐색**: 최대 depth=4, score 기반 ACT Halting으로 관련 없는 탐색 자동 중단
3. **QueryRouter**: 질의를 chat/coding/retrieval로 자동 분류
4. **Memory System**: 사용자 선호도(preference), 반복 패턴(pattern), 목표(goal) 자동 저장
5. **Persona System**: admin이 이름, 성향, 언어, 추가 지시를 설정 → 모든 답변에 반영
6. **보안 3단계**: pre_check → RAG Loop → post_check (ABAC, Instruction Isolation, 출력 필터링)
7. **Patch Pipeline**: 코딩 모드에서 생성된 코드 자동 검증 및 적용 (PENDING_APPROVAL 방식)
8. **멀티모달**: 이미지(EXIF + LLaVA 분석), 영상(OpenCV + Whisper), 오디오 지원
9. **미디어 저장**: 날짜별 자동 분류 + 챗 지시 기반 커스텀 폴더 저장
10. **웹 UI**: 대화형 챗 + 파일 업로드 + Admin 관리 페이지

### 기술 스택
- **LLM**: Gemma (Ollama 로컬 추론) | 코딩: Qwen2.5-Coder:32b | 비전: LLaVA:13b
- **Vector DB**: ChromaDB (로컬)
- **Graph**: Markdown Wiki 기반 Ontology 강제 Graph
- **인증**: JWT + RBAC/ABAC
- **서버**: FastAPI (Python)

## 현재 한계 및 개선 목표

### 현재 한계
- LLM이 로컬(Ollama)이라 응답 속도 6~30초 (GPU 성능 의존)
- Qwen2.5-Coder:32b 첫 로드 시 60초 이상 소요
- 한국어 형태소 분석 없어 BM25 정확도 제한
- 멀티 에이전트 구조 미완성

### 개선 목표 (Phase 8 이후)
- **Self-Learning**: 대화 결과를 자동으로 wiki에 반영
- **Multi-Agent**: 여러 전문 에이전트 협력 시스템
- **실시간 웹 검색**: 외부 정보와 내부 wiki 통합
- **모바일 앱**: 웹 UI에서 모바일 앱으로 확장
- **성능 최적화**: 응답 속도 목표 < 10초

## 설계 원칙

의사결정 우선순위:
1. 보안
2. 데이터 정합성
3. Graph 정확성
4. 안정성
5. 성능
6. 기능 확장

## 정체성

자메스는 단순한 AI가 아니라 **보안이 보장된 지식 추론 엔진**이다.
개발자: PROJECT JAMES 팀
현재 버전: Phase 7 (2026)
"""

def create_james_wiki():
    # concept 폴더 생성
    concept_dir = WIKI_PATH / "prod" / "entity" / "concept"
    concept_dir.mkdir(parents=True, exist_ok=True)

    james_file = concept_dir / "자메스.md"
    james_file.write_text(JAMES_ENTITY_CONTENT, encoding="utf-8")
    print(f"✅ 자메스 entity 생성: {james_file}")

    # Vector Store에도 추가
    try:
        from graph_rag_engine import RAGEngine
        engine = RAGEngine(default_role="admin")
        chunks = [JAMES_ENTITY_CONTENT[:500], JAMES_ENTITY_CONTENT[500:1000],
                  JAMES_ENTITY_CONTENT[1000:1500], JAMES_ENTITY_CONTENT[1500:]]
        engine.vector_store.add_documents_with_meta(
            texts=[c for c in chunks if c.strip()],
            source="자메스.md",
            metadata={
                "sensitivity": "internal",
                "owner":       "system",
                "category":    "시스템",
                "source_type": "prod",
            }
        )
        print(f"✅ Vector Store 등록 완료 ({len([c for c in chunks if c.strip()])} chunks)")
    except Exception as e:
        print(f"⚠️ Vector Store 등록 실패 (서버 없이 실행 시 정상): {e}")
        print("   → 서버 실행 후 자동으로 인식됩니다.")

    print("\n[완료] 이제 자메스에게 다음 질문을 해보세요:")
    print('  "자메스의 기능은 무엇인가?"')
    print('  "자메스의 개선 목표는?"')
    print('  "자메스는 어떤 시스템이야?"')

if __name__ == "__main__":
    create_james_wiki()
