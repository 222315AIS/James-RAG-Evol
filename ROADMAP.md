# Roadmap

> **Note**: This roadmap describes intended directions, not commitments.
> Priorities will shift based on user feedback and real-world testing.

---

## v0.1.0 — Foundation (current, alpha)

**Status**: Released

### Done
- Hybrid Search (Vector + BM25 + keyword)
- Graph-RAG with ontology (12 relation types)
- 3-stage security model (RBAC + ABAC + Instruction Isolation)
- JWT auth + rate limiting + audit log
- Self-evolution scaffolding (Patch Pipeline 4-Gate)
- Multi-LLM routing (Ollama-based)
- Multimodal hooks (image / video / audio)
- Web search (Tavily + DuckDuckGo)
- 11-trait personality system
- Knowledge tracker (8 abilities + 6 domains)
- Internationalization (English + Korean UI)

### Known Gaps (to address in v0.2)
- Real-data validation pending
- Multimodal pipeline integration limited
- Self-evolution untested at scale

---

## v0.2.0 — Real-Data Validation (next, ~2-3 months)

**Theme**: Replace synthetic data with real data; harden weak points.

### Priorities

- **Real-data testing**
  - 30+ real entities across diverse domains
  - User-tested query patterns
  - Edge case discovery and fixing

- **Multimodal completion**
  - Full LLaVA integration for image understanding
  - Whisper integration for audio transcription
  - PDF table extraction improvements

- **Self-evolution proof**
  - Demonstrate end-to-end: feedback → proposal → patch → deploy
  - Quality metrics for evolved patches
  - Rollback mechanism testing

- **Performance**
  - Profile and optimize hot paths
  - Reduce p50/p99 response time
  - Embedding cache improvements

- **Documentation**
  - Tutorial: building a custom domain
  - Tutorial: extending the ontology
  - Architecture deep-dive
  - Video walkthrough

---

## v0.3.0 — Multi-Agent + Graph DB (~6 months)

**Theme**: Scale beyond single-user, optional graph DB backend.

### Priorities

- **Optional Neo4j backend**
  - Migrate from markdown wiki to graph DB
  - Cypher query support
  - Backward compatibility with markdown

- **Multi-agent system**
  - Specialist agents (researcher, coder, security)
  - Agent-to-agent communication
  - Task decomposition + delegation

- **Better evaluation**
  - Automated benchmarking
  - Comparison with other RAG systems
  - Domain-specific accuracy tests

- **API improvements**
  - OpenAI-compatible API for drop-in replacement
  - Streaming responses
  - Webhook support

---

## v1.0.0 — Production Hardening (~12 months)

**Theme**: Enterprise-ready features.

### Priorities

- **Multi-tenancy**
  - Per-tenant data isolation
  - Per-tenant model selection
  - Quota management

- **HTTPS + Production deployment**
  - Default TLS configuration
  - Docker deployment guide
  - Kubernetes Helm charts

- **Compliance preparation**
  - GDPR data deletion support
  - SOC 2 audit log requirements
  - Data residency options

- **Advanced security**
  - Rate limit per role / per endpoint
  - Anomaly detection on audit log
  - Optional 2FA

- **Operational tooling**
  - Backup / restore CLI
  - Migration scripts
  - Health check endpoint
  - Prometheus metrics

---

## Beyond v1.0 — Speculative

Things being considered, no commitment:

- **Federation**: connect multiple JAMES instances
- **On-device fine-tuning**: LoRA adapters per user
- **Edge deployment**: smaller models for embedded use
- **Plugin marketplace**: community-contributed tools
- **Visual graph editor**: web UI for ontology editing
- **Voice interface**: ASR + TTS pipeline

---

## How to Influence the Roadmap

- **GitHub Issues**: feature requests, prioritized by upvotes
- **Discussions**: longer-form proposals
- **Pull Requests**: implement what you need

We prioritize based on:
1. Security-critical fixes (immediate)
2. Real-data feedback from users
3. Strategic alignment with the project's direction
4. Community contribution (volunteer-friendly tasks first)

---

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- `MAJOR.MINOR.PATCH-PRERELEASE`
- `0.x.y` versions may contain breaking changes
- `1.0.0` and beyond will follow strict semver

---

**Last updated**: v0.1.0 release
