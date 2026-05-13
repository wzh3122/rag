# Roadmap

## v1

- FastAPI backend skeleton.
- LangGraph legal QA workflow.
- Configurable LLM / embedding / reranker providers.
- SQLite/PostgreSQL switch through `DATABASE_URL`.
- Qdrant/OpenSearch connection layer.
- RAG empty-index graceful degradation.
- Review Agent safety checks.
- Unit tests and integration-test placeholders.

## v2

- Official legal-source crawler and parser.
- HTML/PDF/DOCX parsing pipeline.
- Legal document, article, chunk, source version, and embedding job tables.
- Batch embedding and Qdrant write jobs.
- OpenSearch BM25 index building.
- Source freshness and effective-status update workflow.

## v3

- Evaluation dataset and regression tests.
- Frontend session UI and source display.
- User system and API token quotas.
- Redis or API Gateway rate limiting.
- Production observability with strict redaction.
- Deployment hardening.

