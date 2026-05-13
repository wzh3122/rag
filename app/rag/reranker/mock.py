class MockRerankerProvider:
    async def rerank(self, query: str, documents: list[dict], top_k: int = 8) -> list[dict]:
        return documents[:top_k]

