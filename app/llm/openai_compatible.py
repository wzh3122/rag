import httpx

from app.config import Settings


class OpenAICompatibleLLMClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def chat(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.2,
        response_format: str | None = None,
    ) -> str:
        if not self.settings.llm_api_key:
            raise RuntimeError("LLM_API_KEY is not configured.")

        payload: dict = {
            "model": self.settings.llm_model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format:
            payload["response_format"] = {"type": response_format}

        url = self.settings.llm_base_url.rstrip("/") + "/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.settings.llm_api_key}"}
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

