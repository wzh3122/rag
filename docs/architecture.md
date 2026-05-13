# Architecture

## Layers

FastAPI exposes `/legal-qa` and `/legal-qa/stream`. `LegalQAService` creates or loads a session, invokes the LangGraph workflow, persists safe summaries, and returns a normalized response.

## Workflow

LangGraph nodes:

1. `fact_extraction`: rule-based domain inference, fact extraction, out-of-scope detection, clarification detection, conflict detection.
2. `legal_retrieval`: plans a query and calls hybrid RAG.
3. `answer_generation`: emits `completed` when sources exist, otherwise `general_reference`.
4. `reviewer`: blocks missing disclaimers, unsupported source use, obsolete/low authority sources, and invalid answer structure.

## RAG

`HybridLegalSearchClient` combines:

- `QdrantSearchClient` for semantic recall.
- `OpenSearchSearchClient` for BM25 / exact keyword recall.
- Embedding provider abstraction.
- Reranker provider abstraction.

When `RAG_INDEX_READY=false` or external services fail, retrieval returns an empty list and the system degrades to `general_reference`.

## Providers

LLM, embedding, and reranker each expose a small protocol plus `mock` and `openai_compatible` implementations. Users configure their own API Key in local `.env`; no author key is stored in this project.

## Database

`DATABASE_URL` supports SQLite and PostgreSQL. v1 tables:

- `qa_sessions`
- `chat_messages`
- `agent_traces`
- `legal_sources`

Production defaults should avoid saving chat raw text and only keep minimal state and redacted summaries.

## Security Boundary

The repository must not contain `.env`, real API keys, production database credentials, user chats, raw traces, logs, database dumps, paid service data, or copied full web pages. Trace persistence uses sanitization helpers and stores summaries rather than raw provider payloads.

