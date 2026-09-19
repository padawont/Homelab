---
title: "Run open-weight AI models on local machine"
status: draft
author: "padawont"
date: 2026-09-19
tags: [local-ai, self-hosting, inference, gpu]
technologies: [ollama, llama-cpp, open-webui]
related_ideas: []
---

# Run open-weight AI models on local machine

## Objective

Self-host open-weight LLMs on the local workstation so inference stays local —
no API keys, no per-token cost, no data leaving the machine.

## Current Specs

- CPU: AMD Ryzen 7 5800X3D — 8C/16T, 3D V-Cache
- RAM: 31 GiB total (~24 GiB available)
- GPU: AMD Radeon RX 5700 XT (RDNA1, Navi 10) — 8 GiB VRAM, `amdgpu` driver
- Disk: 220 GB, 182 GB free
- OS: CachyOS Linux, kernel 7.2.6
- Runtime: Docker 29.8.1; no ROCm, no NVIDIA tooling

## Notes

- 8 GiB VRAM fits Q4 7B–8B models; larger models partly offloaded to CPU.
- No ROCm on this GPU — RDNA1 support is unofficial, so llama.cpp's Vulkan
  backend is the likely path. Ollama is the simplest option.
- Runs on this workstation under Docker, not the k3s node.

## Open Questions

- Which serving stack performs best here: llama.cpp Vulkan or Ollama?
