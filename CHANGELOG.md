# Changelog

All notable changes to PROJECT JAMES will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.1] — Path Auto-Detection (Patch)

### Fixed

#### Critical: Hardcoded Paths Removed
- **config.py**: `BASE_DIR` was hardcoded. Now auto-detected from `config.py`'s own location.
- **config.py**: Removed hardcoded user paths exposing the developer's Windows username.
- **vector_store.py**: `LOCAL_MODEL_PATH` was hardcoded. Now derives from `BASE_DIR`. Fixes the issue where renaming the project folder caused the embedding model to be re-downloaded externally.
- **patch_abac_fields.py / tools/admin/seed_data.py / tools/admin/wiki_reset.py**: Replaced hardcoded fallback paths with location-relative detection.

#### Cross-Platform Support
- Tesseract OCR path: auto-detected for Windows / macOS / Linux
- Poppler path: auto-detected for Windows; uses system PATH on macOS / Linux
- Ollama path: uses system PATH (no hardcoded location)

### Added
- Environment variable overrides for all binary paths:
  - `TESSERACT_PATH` — Tesseract binary
  - `JAMES_POPPLER_PATH` — Poppler bin directory
  - `OLLAMA_PATH` — Ollama binary
  - `JAMES_MODEL_PATH` — Sentence-Transformer model location
  - `JAMES_LLM_MODEL` — Default LLM model name (default: `gemma2:2b`)
  - `OLLAMA_API_URL` — Ollama API endpoint
  - `JAMES_MAX_UPLOAD_MB` — Upload size limit (default: 100)

### Security
- **CRITICAL**: Previous version (v0.1.0) included paths revealing the developer's local Windows username. Anyone cloning the repository could see this information. Now removed.
- Project folder can be renamed/moved freely without breaking functionality.
- Anyone cloning the repository can run `python server_llmwiki.py` immediately without editing paths.

### Migration from v0.1.0
No migration steps needed. The fix is backward compatible:
- Existing installations will continue to work
- Folder rename now safe
- No database / data changes required

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
- 3-stage access control (Vector / Graph / Output)
- RBAC with 4 roles
- ABAC with 4 sensitivity levels
- 31+ prompt injection pattern detection
- Instruction Isolation framework
- JWT authentication
- Rate limiting (30 req/60s)
- Full audit log in SQLite

#### Knowledge Management
- Markdown-based wiki as knowledge graph
- File ingestion (PDF, DOCX, images, video, audio)
- Automatic entity extraction and linking
- Relations stored in YAML frontmatter

#### Self-Evolution Scaffolding
- Patch Pipeline with 4-Gate validation
- 11-trait personality system
- Knowledge tracker (8 abilities + 6 domains)
- Feedback engine

#### Multimodal & Tools
- LLaVA, Whisper, ffmpeg, pytesseract, easyocr integrations
- Sandboxed Python execution
- File upload pipeline

#### Web Search
- Tavily (primary) + DuckDuckGo (fallback)

#### User Interface
- Web-based chat UI + Admin dashboard
- Session management
- Reasoning path visualization
- Confidence badges

#### Internationalization
- 286 i18n keys (English / Korean)
- Default language: English
- Live toggle (KO / EN)

#### Documentation
- README.md, README.ko.md
- SECURITY.md, ROADMAP.md, CONTRIBUTING.md, CHANGELOG.md
- .env.example

---

## Unreleased

See [ROADMAP.md](ROADMAP.md) for v0.2.0 plan.

---

[0.1.1]: https://github.com/Hashevolution/James-RAG-Evol/releases/tag/v0.1.1
[0.1.0-alpha]: https://github.com/Hashevolution/James-RAG-Evol/releases/tag/v0.1.0-alpha
