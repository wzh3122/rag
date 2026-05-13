from typing import Protocol


class RerankerProvider(Protocol):
    async def rerank(self, query: str, documents: list[dict], top_k: int = 8) -> list[dict]:
        ...

