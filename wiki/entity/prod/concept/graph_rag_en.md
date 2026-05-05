---
entity_id: concept_graph_rag_en
entity_type: concept
name: Graph-RAG
normalized_name: graph-rag
aliases:
  - Graph Retrieval-Augmented Generation
  - Knowledge Graph RAG
sensitivity: public
owner: system
source_type: test
domain: science
relations:
  - target: Vector Search
    type: USES
    weight: 1.0
  - target: Ontology
    type: BELONGS_TO
    weight: 1.2
  - target: Knowledge Graph
    type: BELONGS_TO
    weight: 1.2
---

## Summary
Graph-RAG (Graph Retrieval-Augmented Generation) is an advanced AI architecture
that combines traditional vector-based retrieval with graph-structured knowledge
reasoning. Unlike pure vector search, Graph-RAG traverses explicit relationships
between entities to produce explainable, hallucination-reduced answers.

## Key Concepts
- **Graph traversal**: DFS/BFS over entity relations with confidence scoring
- **Ontology enforcement**: Relations validated against predefined schemas
- **Hybrid search**: Vector (60%) + BM25 (20%) + keyword (20%) fusion
- **Reasoning paths**: Explicit trace of how an answer was derived
- **Sensitivity gating**: Access control at the relation level

## How JAMES Uses It
JAMES implements Graph-RAG with:
1. Markdown-based wiki as the knowledge graph
2. DFS traversal with depth ≤ 4 and confidence threshold
3. 12-type ontology (BELONGS_TO, STUDIES, WORKS_AT, etc.)
4. 3-stage security filter across the RAG pipeline

## Related Keywords
Graph-RAG, knowledge graph, retrieval, ontology, hallucination reduction, reasoning
