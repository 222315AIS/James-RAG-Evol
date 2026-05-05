# Changelog

All notable changes to PROJECT JAMES will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0-alpha] — Initial Release

### Added

#### Core Engine
- Hybrid Search (Vector 60% + BM25 20% + keyword 20%)
- Graph-RAG with 12 ontology relation types
- DFS traversal with confidence-based pruning
- ChromaDB vector store with Sentence-Transformers embeddings
- Ollama-based local LLM execution

#### Security
- 3-stage access control (Vector → Graph → Output)
- RBAC with 4 roles (admin / manager / employee / external)
- ABAC with 4 sensitivity levels (public / internal / confidential / secret)
- 31+ prompt injection pattern detection
- Instruction Isolation framework
- JWT authentication with HS256 signing
- Rate limiting (30 req/60s)
- Full audit log in SQLite

#### Knowledge Management
- Markdown-based wiki as knowledge graph
- Auto-generation of entity files via `wiki_generator.py`
- File ingestion (PDF, DOCX, images, video, audio)
- Automatic entity extraction and linking
- Relations stored in YAML frontmatter

#### Self-Evolution Scaffolding
- Patch Pipeline with 4-Gate validation
- 11-trait personality system (Curiosity, Focus, Caution, etc.)
- Knowledge tracker (8 abilities + 6 domains)
- Feedback engine (👍/👎 → proposal generation)
- Reject reason → long-term memory storage

#### Multimodal & Tools
- LLaVA integration for image understanding
- Whisper for audio transcription
- ffmpeg for video processing
- pytesseract + easyocr for OCR
- pdf2image + PyPDF2 for PDF processing
- Sandboxed Python execution
- File upload pipeline

#### Web Search
- Tavily integration (primary, AI-focused)
- DuckDuckGo fallback
- Domain-aware result filtering
- Quality content validation
- URL fetch with content extraction

#### Multi-LLM Routing
- Query router (chat / coding / retrieval / web_search)
- Provider abstraction (`llm/providers/`)
- Hardware-based model recommendation
- Auto-installation via Ollama API

#### User Interface
- Web-based chat UI (vanilla JS)
- Admin dashboard with live metrics
- Session management
- File upload with progress
- Reasoning path visualization
- Confidence badges
- Toast notifications for actions

#### Internationalization
- 286 i18n keys across English and Korean
- Default language: English (global accessibility)
- Live toggle (KO ↔ EN) without page reload
- Dynamic system prompt language switching
- LLM response language follows UI language

#### Documentation
- README.md (English)
- README.ko.md (Korean)
- SECURITY.md (security model + threat model)
- ROADMAP.md (development plan)
- CONTRIBUTING.md (contribution guide)
- CHANGELOG.md (this file)
- .env.example (configuration template)

### Security Notes
- Default JWT secret is a placeholder; **must be replaced** before non-development use
- HTTPS not configured by default; reverse proxy required for production
- Single-tenant only; multi-tenancy planned for v1.0

### Known Limitations
- Real-data validation pending (synthetic data only)
- Self-evolution scaffolded but not proven end-to-end
- Multimodal pipeline integration limited
- No automated benchmarking yet

---

## Unreleased

### Planned for v0.2.0
See [ROADMAP.md](ROADMAP.md) for full plan.

- Real-data validation across 30+ entities
- Multimodal pipeline completion
- Self-evolution end-to-end demonstration
- Performance profiling and optimization
- Tutorial documentation

---

[0.1.0-alpha]: https://github.com/Hashevolution/James-RAG-Evol/releases/tag/v0.1.0-alpha
