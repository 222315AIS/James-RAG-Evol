---
entity_id: concept_security_reasoning_en
entity_type: concept
name: Security Reasoning
normalized_name: security-reasoning
aliases:
  - AI Security Layer
  - RBAC ABAC Security
sensitivity: public
owner: system
source_type: test
domain: security
relations:
  - target: RBAC
    type: BELONGS_TO
    weight: 1.2
  - target: ABAC
    type: BELONGS_TO
    weight: 1.2
  - target: Prompt Injection
    type: STUDIES
    weight: 1.0
---

## Summary
Security Reasoning is the discipline of embedding security controls directly into
AI inference pipelines — treating security as a design principle rather than a
post-hoc feature. JAMES implements a 3-stage security model that filters at the
input, graph, and output layers.

## Key Concepts
- **RBAC** (Role-Based Access Control): 4 roles — admin, manager, employee, external
- **ABAC** (Attribute-Based Access Control): 4 sensitivity levels — public, internal, confidential, secret
- **Instruction Isolation**: Separates user commands from data content to prevent injection
- **PII Masking**: Removes personally identifiable information from outputs
- **Audit Logging**: Full activity trace in SQLite for compliance

## Threat Model
- Defends against: prompt injection, privilege escalation, data leakage
- Partial defense: tool abuse, memory poisoning
- Out of scope: network attacks, physical access, compromised LLM weights

## Related Keywords
RBAC, ABAC, prompt injection, jailbreak, PII, audit log, zero-trust
