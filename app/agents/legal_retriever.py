from app.agents.query_planner import plan_search_query
from app.rag.hybrid_search import HybridLegalSearchClient


async def retrieve_sources(message: str, legal_domain: str, region: str | None):
    client = HybridLegalSearchClient()
    return await client.search(plan_search_query(message, legal_domain, region))

