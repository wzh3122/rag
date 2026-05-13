import httpx

from app.config import Settings


class OpenAICompatibleRerankerProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def rerank(self, query: str, documents: list[dict], top_k: int = 8) -> list[dict]:
        if not self.settings.reranker_api_key:
            raise RuntimeError("RERANKER_API_KEY is not configured.")
        url = self.settings.reranker_base_url.rstrip("/") + "/v1/rerank"
        payload = {
            "model": self.settings.reranker_model,
            "query": query,
            "documents": documents,
            "top_k": top_k,
        }
        headers = {"Authorization": f"Bearer {self.settings.reranker_api_key}"}
        async with httpx.AsyncClient(timeout=self.settings.reranker_timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        return data.get("results", [])[:top_k]

