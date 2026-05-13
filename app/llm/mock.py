class MockLLMClient:
    async def chat(
        self,
        messages: list[dict],
        *,
        temperature: float = 0.2,
        response_format: str | None = None,
    ) -> str:
        last = messages[-1]["content"] if messages else ""
        if response_format == "json_object":
            return '{"summary": "mock response", "input": "' + str(last)[:50].replace('"', '\\"') + '"}'
        return "这是 mock LLM 响应。"

