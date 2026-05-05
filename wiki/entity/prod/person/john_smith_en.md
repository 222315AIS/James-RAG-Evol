---
entity_id: person_john_smith_en
entity_type: person
name: John Smith
normalized_name: john-smith
aliases:
  - J. Smith
sensitivity: internal
owner: system
source_type: test
domain: general
relations:
  - target: JAMES Research Lab
    type: BELONGS_TO
    weight: 1.2
  - target: Security Reasoning
    type: STUDIES
    weight: 1.0
---

## Summary
John Smith is a sample entity used for testing JAMES's knowledge retrieval,
relation graph traversal, and access control features. This is a synthetic
test entity — not a real person.

## Background
- Role: Senior Security Researcher
- Organization: JAMES Research Lab
- Expertise: Prompt injection defense, RBAC/ABAC design
- Projects: Graph-RAG security pipeline, ontology design

## Notes
This entity is part of the English seed dataset for JAMES v0.1.0.
It demonstrates that JAMES can handle English-language person entities
alongside Korean ones.

## Related Keywords
sample entity, test data, security researcher, person
