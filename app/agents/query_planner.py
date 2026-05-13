from app.rag.schemas import SearchQuery


def plan_search_query(message: str, legal_domain: str, region: str | None) -> SearchQuery:
    return SearchQuery(query=message, legal_domain=legal_domain, region=region, top_k=8)

