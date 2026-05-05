---
entity_id: org_james_research_lab_en
entity_type: org
name: JAMES Research Lab
normalized_name: james-research-lab
aliases:
  - JRL
  - JAMES Lab
sensitivity: internal
owner: system
source_type: test
domain: general
relations:
  - target: Graph-RAG
    type: STUDIES
    weight: 1.0
  - target: Security Reasoning
    type: STUDIES
    weight: 1.0
  - target: John Smith
    type: WORKS_AT
    weight: 1.0
---

## Summary
JAMES Research Lab (JRL) is a fictional organization used as sample data
to demonstrate JAMES's organization-level entity handling, relation traversal,
and access control. This is a synthetic test entity.

## Focus Areas
- Local AI inference and privacy-preserving architectures
- Graph-RAG with ontology enforcement
- Security-first AI design (RBAC, ABAC, Instruction Isolation)
- Self-evolving AI systems through feedback loops

## Notes
Part of the English seed dataset for JAMES v0.1.0.
Demonstrates org-level entity support alongside person and concept entities.

## Related Keywords
organization, sample entity, AI lab, research, security
