from pydantic import BaseModel


class SearchQuery(BaseModel):
    query: str
    legal_domain: str = "unknown"
    region: str | None = None
    top_k: int = 8


class SearchResult(BaseModel):
    title: str
    url: str | None = None
    source: str | None = None
    snippet: str | None = None
    quote_text: str | None = None
    authority_level: str = "unknown"
    effective_status: str = "unknown"
    basis_type: str = "law"
    relevance_score: float = 0.0
    used_for: str | None = None

