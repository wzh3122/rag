import hashlib

from app.config import get_settings


class MockEmbeddingProvider:
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        dimension = get_settings().embedding_dimension
        vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            values = [(digest[i % len(digest)] / 255.0) for i in range(dimension)]
            vectors.append(values)
        return vectors

