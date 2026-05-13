from typing import Protocol


class LLMClient(Protocol):
    async def chat(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.2,
        response_format: str | None = None,
    ) -> str:
        ...

