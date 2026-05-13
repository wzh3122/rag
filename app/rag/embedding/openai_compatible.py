import httpx

from app.config import Settings


class OpenAICompatibleEmbeddingProvider:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self.settings.embedding_api_key:
            raise RuntimeError("EMBEDDING_API_KEY is not configured.")
        url = self.settings.embedding_base_url.rstrip("/") + "/v1/embeddings"
        payload = {"model": self.settings.embedding_model, "input": texts}
        headers = {"Authorization": f"Bearer {self.settings.embedding_api_key}"}
        async with httpx.AsyncClient(timeout=self.settings.embedding_timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]

