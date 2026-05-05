---
entity_id: concept_ollama_en
entity_type: concept
name: Ollama
normalized_name: ollama
aliases:
  - Local LLM Runner
  - Ollama AI
sensitivity: public
owner: system
source_type: test
domain: science
relations:
  - target: Gemma
    type: USES
    weight: 1.0
  - target: LLM
    type: BELONGS_TO
    weight: 1.2
---

## Summary
Ollama is an open-source tool for running large language models (LLMs) locally
on consumer hardware. It provides a simple REST API (OpenAI-compatible) and
supports models like Gemma, LLaVA, Mistral, DeepSeek-Coder, and many others.
JAMES uses Ollama as its primary LLM backend for 100% local inference.

## Key Features
- Zero cloud dependency — all inference runs on-device
- REST API on localhost:11434
- Model management: pull, run, delete via API or CLI
- Supports multimodal models (LLaVA for image+text)
- GPU acceleration via CUDA/Metal/ROCm

## JAMES Integration
- Default model: gemma4:e4b (fast, low VRAM)
- Coding tasks: deepseek-coder
- Multimodal: llava:13b
- Auto-recommendation based on hardware specs (VRAM/RAM)

## Related Keywords
Ollama, local LLM, Gemma, LLaVA, on-device AI, self-hosted, inference
