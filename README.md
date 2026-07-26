# Abdelrahman Abouroumia

AI & Backend Engineer. Co-founder of [Zaylon AI](https://zaylon.ai). I build backend systems, and the retrieval and agent layers that run on top of them. B.Sc. in Computer and Communications Engineering with an AI concentration from Alexandria University.

[romia.dev](https://romia.dev) &nbsp;·&nbsp; [Resume](https://romia.dev/resume.pdf) &nbsp;·&nbsp; [LinkedIn](https://linkedin.com/in/abdelrahman-abouroumia) &nbsp;·&nbsp; [Hugging Face](https://huggingface.co/Ab-Romia) &nbsp;·&nbsp; [aabouroumia@gmail.com](mailto:aabouroumia@gmail.com)

---

## AI agents and RAG

**[Zaylon AI](https://zaylon.ai)** &nbsp; `LangGraph · FastAPI · PostgreSQL · Redis · Docker`

Conversational commerce for MENA merchants: customers browse, ask, and check out by chatting on WhatsApp, Instagram, Messenger, TikTok, or web chat. One tool-calling agent with about 30 scoped tools across sales, support, and checkout, connected to six e-commerce platforms and three payment providers. It started as a multi-agent supervisor routing to specialists, and I consolidated it into a single agent because the routing layer was the least reliable part of the system. The NLP side reads English, Egyptian Arabic, and Franco-Arabic, and replies in whichever one the customer used. Multi-tenant with row-level isolation, deployed on Railway.

**[Talos](https://github.com/Ab-Romia/talos)** &nbsp; `FastAPI · Milvus · MinIO · taskiq · LangChain`

Team chat platform with a workspace-grounded assistant that answers from the team's own documents and cites the page it used. Files ingest asynchronously, chunked by heading and embedded with bge-small; a question runs dense and BM25 retrieval fused with reciprocal rank fusion, then a cross-encoder reranker, and the answer streams back with inline citations. An MCP server and a Slack bot serve the same corpus. Team graduation project, grade A+; my track was the AI, retrieval, evaluation, and deployment.

When the assistant gave weak answers I traced it to the chunker, which had shredded a 90-page guide into 1,778 fragments with a median length of 67 characters. I wrote 83 questions with page-level gold labels and ran a paired, Holm-corrected experiment on the production pipeline. Judged answer correctness went from 0.657 to 0.855 on that workspace's own corpus, which is a document-specific result and not a public benchmark. [Case study](https://romia.dev/projects/talos).

**[ContextIQ-RAG](https://github.com/Ab-Romia/ContextIQ-RAG)** &nbsp; `fastembed/ONNX · bm25s · cross-encoder`

A RAG pipeline that runs on free CPU, written to be read: bge-small dense embeddings and BM25 fused with RRF, contextual chunk headers, cross-encoder reranking, inline citations, streaming. The evaluation reports where each arm loses. Over 21 questions on a corpus of seven handbooks, dense-only retrieval was the weakest at hit@3 0.67, hybrid took the best recall at 0.94, and adding the reranker gave the best hit@3 at 0.83 with MRR 0.78. [Demo](https://huggingface.co/spaces/Ab-Romia/Context-Aware-AI) &nbsp;·&nbsp; [Write-up](https://romia.dev/blog/contextiq-hybrid-rag-retrieval).

## Backend and distributed systems

**[Virtual-Bank-System](https://github.com/Ab-Romia/Virtual-Bank-System)** &nbsp; `Java 21 · Spring Boot · Kafka · PostgreSQL`

A gateway and four services running a Kafka transfer saga with a transactional outbox, idempotent consumers, a dead-letter queue, and pessimistic locking, secured with RS256 JWT and traced with OpenTelemetry. A Testcontainers test fires twenty simultaneous transfers at one account and proves no double-spend. [Write-up](https://romia.dev/blog/event-driven-bank-transfer-saga).

## Applied ML

**[RAVDESS-emotion-recognition](https://github.com/Ab-Romia/RAVDESS-emotion-recognition)** &nbsp; `PyTorch · WavLM-large`

Speech emotion recognition evaluated actor-disjoint across six folds, so no speaker appears in both training and test. A frozen WavLM-large encoder with learnable layer weighting and attentive statistics pooling reaches 70.3% on audio alone, and calibrated late fusion with a facial-expression model reaches 78.8%. The project exists because of the split: moving the first audio model I tested off a random split and onto an actor-disjoint one cost it 13 points, which is the difference between measuring emotion and measuring whose voice it is. A unit test fails the build if any actor leaks across folds. [Demo](https://huggingface.co/spaces/Ab-Romia/RAVDESS-emotion-recognition) &nbsp;·&nbsp; [Write-up](https://romia.dev/blog/speaker-leakage-ravdess).

**[VoicePrint](https://github.com/Ab-Romia/VoicePrint)** &nbsp; `Python · StyleDistance · NLP`

Authorship stylometry from a StyleDistance style embedding plus interpretable function-word features. A 130-dimensional vector of function words, holding no content words at all, separated five authors at 0.684 macro-F1 and 0.889 accuracy against a five-class baseline of 0.20, with the splits taken by work so no book appears on both sides. [Write-up](https://romia.dev/blog/measuring-a-writing-voice).

---

The portfolio itself is open source at [Ab-Romia/romia.dev](https://github.com/Ab-Romia/romia.dev): Next.js 16 App Router, React 19, TypeScript, Tailwind v4. It carries the case studies and write-ups linked above, plus a couple of playable demos.

## Skills

```text
skills
├── ai/ml       LangGraph · LangChain · PyTorch · RAG · reranking
├── backend     FastAPI · Spring Boot · Kafka · microservices
├── retrieval   Milvus · ChromaDB · pgvector · BM25 · ONNX
├── data        PostgreSQL · Redis
├── frontend    React · Next.js · TypeScript · Tailwind
├── languages   Python · Java · TypeScript · SQL · C/C++
└── devops      Docker · GitHub Actions · CI/CD · Linux · Railway
```

English and Arabic fluently, German and Spanish at a conversational level.
