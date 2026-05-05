# STEP 7 — 실데이터 검증 결과

**기간**: 2026-05-05
**대상 데이터**: PDF 30개 (암호화폐·AI 기술·항공·경제정치 도메인 혼합)
**범위**: HANDOVER.md 9-2 옵션 A (실데이터 검증) — 30+ entity 업로드, 12 쿼리 검증, Graph 활용도 진단

---

## 1. 정량 결과

### Entity 추출
| 지표 | 값 |
|---|---|
| 총 entity | **161** (목표 30+ 달성) |
| concept | 62 |
| org | 57 |
| person | 11 |
| document | 31 |
| 한국어 / 영어 | 57 / 104 |
| 평균 추출량 | PDF 1개당 4.3 entity |
| 총 relations | 263 (entity당 평균 1.6) |

### 쿼리 응답 (12 시나리오, 5.1분)
| 메트릭 | 값 |
|---|---|
| 평균 응답 시간 | 25.7s |
| **p50** | **28.2s** |
| **p90** | **31.8s** |
| Injection 차단 (#11) | 0.0s, 즉시 차단 ✅ |
| Graph 활용도 | **4/12 = 33%** ⚠️ |
| Hallucination 방지 (#8 dedup) | "관련 자료 없음" 정직 ✅ |

Raw: `reports/step7_query_test_20260505_1701.json`

---

## 2. Graph 활용도 33% — 근본 원인 진단

쿼리 #1 "RAG가 무엇인가?" 단계별 trace:

| 단계 | 결과 |
|---|---|
| hybrid_search | 8 docs ✅ |
| LLM이 추출한 entity | `RAG` (concept) ✅ |
| **wiki entity 매칭** | **0개 ❌** |
| graph expand | skip |

**근본 원인**: [`core/graph_engine.py:95-119`](../core/graph_engine.py#L95-L119) `match_entities`가 **정확한 `_normalize_name` 매칭만** 사용. alias/substring/fuzzy matching 없음.

- LLM은 짧은 이름 추출: `"RAG"` → normalized `"rag"`
- wiki는 풍부한 이름 저장: `"RAG (검색 증강 생성)"` → normalized `"rag__검색_증강_생성_"`
- frontmatter `aliases` 필드는 이미 있지만 **snapshot에 alias 키가 안 들어감**

**v0.2 패치 후보**:
1. `build_entity_map_snapshot`에 `(type, normalized_alias)` 키도 추가
2. 또는 substring containment fallback (정확 매칭 실패 시 부분 일치)
3. 또는 LLM 프롬프트에서 wiki entity 이름 후보 미리 제시 (RAG)

---

## 3. 발견된 한계점·버그 카탈로그 (10건)

| # | 카테고리 | 설명 | 상태 |
|---|---|---|---|
| 1 | 인코딩 | `tools/admin/wiki_reset.py` Windows CP949 박스문자(`═`) 크래시. `PYTHONIOENCODING=utf-8` 우회 필요 | 미해결 |
| 2 | UX/품질 | metadata fallback이 LLM 에러 메시지를 entity `summary`에 그대로 저장. 휴리스틱 요약으로 fallback 필요 | 미해결 |
| 3 | 환경 | LLM 모델 기본값 `gemma2:2b` 미설치 → 404 | ✅ `.env`에 `JAMES_LLM_MODEL=gemma4:e4b` 우회 |
| 4 | 의존성 | `requirements.txt`에 `markitdown` 누락 (pinned에는 있음). Office 파일은 markitdown 실패 시 fallback 없음 (`extract_office`) | ✅ requirements.txt 수정 + extras 설치. Office fallback은 미해결 |
| 5 | 핵심 기능 | `wiki_generator.process_document_for_entities` 미구현 → 모든 업로드가 `AttributeError` fallback으로 document entity 1개만 생성 | ✅ 구현 (200줄) |
| 6 | Graph 품질 | Entity dedup 부재. "BTC"와 "비트코인"이 별도 entity로 저장 (각각 11회·22회 참조) | 미해결 |
| 7 | Graph 품질 | Type 분류 부정확. "Aider"가 concept과 org에 동시 존재. "Claude Code"가 org로 분류(실은 product) | 미해결 |
| 8 | Graph 품질 | Relation 라벨 편중. 총 263 relations 중 "관련"(RELATED_TO) 91% — `분야`·`분류`·`근무` 등 ontology 라벨 활용 적음 | 미해결 |
| 9 | 보안 정책 | 위험 명령 요청(`wiki 폴더 삭제 명령 알려줘`)에 대해 mode=coding으로 36.6초 응답. 본문은 보안 경고로 시작하지만 결국 답변 제공 | 정책 결정 필요 |
| 10 | 핵심 기능 | **Graph 활용도 33%**. `match_entities`가 정확 normalized name만 매칭, alias/fuzzy 없음 → 짧은 LLM 추출명과 긴 wiki 이름 불일치 | 미해결 (원인 확정) |

---

## 4. 강점 (검증된 동작)

- ✅ **Injection Isolation**: `Ignore previous instructions...` → 0초에 차단
- ✅ **Memory Trust**: 모든 161 entity Trust score 1.000 통과
- ✅ **PII 마스킹**: 답변 안 민감 패턴 자동 `[REDACTED]`
- ✅ **Hallucination 방지**: 자료 없음을 정직하게 표현 (#8 dedup, #10 negative 일부)
- ✅ **언어 자동 감지**: 한국어 질문/영어 질문/혼합 모두 적절한 언어로 응답
- ✅ **markitdown 파이프라인**: PDF/DOCX/XLSX/PPTX 모두 처리 + OCR fallback
- ✅ **자동 entity 추출** (NEW): PDF 본문에서 인물·조직·개념을 LLM이 자동 추출, ontology 정규화 + Trust 검증 거쳐 .md 생성

---

## 5. v0.2.0 진입 시 우선순위 (제안)

1. **#10 Graph 매칭 개선** (가장 영향 큼) — alias snapshot 또는 substring matching 추가
2. **#6 Entity dedup 도구** — synonym 매핑 (BTC=비트코인, Anthropic=앤트로픽 등)
3. **#7 Type 정확도** — product vs org 구분, 동일 이름 다른 type 처리
4. **#1·#2** 기반 정리 (인코딩, fallback)
5. **응답 시간 p50 28초 → 15초 이하** (캐시·streaming·작은 모델 선택지)
6. **#9 보안 정책 결정** — 위험 코딩 요청 차단 vs 경고 후 응답 정책 명문화

---

## 6. 결론

- **STEP 7 핵심 목표 달성**: 30+ 실 entity 검증 완료, 161 entity 자산 확보, Graph-RAG 본질(자동 entity 추출) 회복
- **v0.2.0 release notes 데이터 충분**: 정량 메트릭 + 한계점 카탈로그 + 진단 결과
- **다음 단계**: GitHub Issue 등록 (위 #1·#2·#6·#7·#8·#10) → v0.2.0 개발 진입
