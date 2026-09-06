# Abdelrahman Abouroumia (Romia)

Software Engineer at Tutanic. Co-founder of [Zaylon AI](https://zaylon.ai). I build backend services and the retrieval and agent layers that run on them. B.Sc. in Computer and Communications Engineering with an AI concentration, Alexandria University.

[romia.dev](https://romia.dev) &nbsp;·&nbsp; [Resume](https://romia.dev/resume.pdf) &nbsp;·&nbsp; [LinkedIn](https://linkedin.com/in/abdelrahman-abouroumia) &nbsp;·&nbsp; [Hugging Face](https://huggingface.co/Ab-Romia) &nbsp;·&nbsp; [aabouroumia@gmail.com](mailto:aabouroumia@gmail.com)

---

## AI Engineering

**[Zaylon AI](https://zaylon.ai)** &nbsp; `LangGraph · FastAPI · PostgreSQL · Redis · Docker`

Conversational commerce for MENA merchants: customers browse, ask, and check out by chatting on WhatsApp, Instagram, Messenger, TikTok, or web. One tool-calling agent across sales, support, and checkout. It began as a multi-agent supervisor and I consolidated it into a single agent, because the routing layer was the least reliable part of the system.

**[Talos](https://github.com/Ab-Romia/talos)** &nbsp; `FastAPI · Milvus · taskiq · bge-small`

Team chat platform with a workspace-grounded assistant that answers from the team's own documents and cites the page it used. Weak answers traced to the chunker rather than the model, and I measured the fix with a labelled question set and a paired experiment instead of by feel. Graduation project, grade A+. [Case study](https://romia.dev/projects/talos)

**[commentdraft](https://github.com/Ab-Romia/commentdraft)** &nbsp; `Python · CLI · PyPI · Apache-2.0`

Published CLI from paid client work: it reads the comments on a creator's own posts and drafts replies grounded in one source document, escalating anything that document does not cover rather than guessing. Nothing publishes until a person approves that specific reply, and the gate is structural rather than a setting. Ships connection guides for eight platforms, researched from their own primary documentation. [PyPI](https://pypi.org/project/commentdraft/) &nbsp;·&nbsp; [Guides](https://romia.dev/commentdraft)

## Backend and distributed systems

**[Virtual-Bank-System](https://github.com/Ab-Romia/Virtual-Bank-System)** &nbsp; `Java 21 · Spring Boot · Kafka · PostgreSQL`

A gateway and four services running a Kafka transfer saga with a transactional outbox, idempotent consumers, a dead-letter queue, and pessimistic locking. A concurrency test fires simultaneous transfers at one account and proves no double-spend. [Write-up](https://romia.dev/blog/event-driven-bank-transfer-saga)

## Applied ML

**[RAVDESS-emotion-recognition](https://github.com/Ab-Romia/RAVDESS-emotion-recognition)** &nbsp; `PyTorch · WavLM-large`

Speech emotion recognition evaluated actor-disjoint, so no speaker appears in both training and test. Moving my first model off a random split cost it thirteen points, which is the difference between measuring emotion and measuring whose voice it is, and a unit test now fails the build if any actor leaks. [Demo](https://huggingface.co/spaces/Ab-Romia/RAVDESS-emotion-recognition) &nbsp;·&nbsp; [Write-up](https://romia.dev/blog/speaker-leakage-ravdess)

Also [ContextIQ-RAG](https://github.com/Ab-Romia/ContextIQ-RAG), a CPU-only hybrid RAG pipeline written to be read, and [VoicePrint](https://github.com/Ab-Romia/VoicePrint), authorship stylometry from function words alone.

## Open source

- **[Kludex/starlette#3474](https://github.com/Kludex/starlette/pull/3474)** &nbsp; merged. Documented a nested-mutation behaviour I found reading the request stack, with the Flask and Django precedent for it.
- **[chatwoot/chatwoot#15602](https://github.com/chatwoot/chatwoot/pull/15602)** &nbsp; open. A three-line fix with a spec, watched failing on pristine `develop` before the fix existed.

## Skills

```text
skills
├── ai          LLM agents · RAG · MCP · LangGraph · LangChain
├── ml          PyTorch · embeddings · reranking · evaluation
├── backend     FastAPI · Spring Boot · Kafka · microservices
├── data        PostgreSQL · pgvector · Redis · Milvus
├── languages   Python · Java · TypeScript · SQL · C/C++
└── devops      Docker · GitHub Actions · CI/CD · Linux · Railway
```

English and Arabic fluently, German and Spanish at a conversational level.

The portfolio itself is open source at [Ab-Romia/romia.dev](https://github.com/Ab-Romia/romia.dev).
