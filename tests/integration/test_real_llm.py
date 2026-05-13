import os

import pytest

from app.llm.factory import get_llm_client


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION_TESTS") != "true", reason="integration tests are opt-in")
@pytest.mark.asyncio
async def test_real_llm_chat():
    client = get_llm_client()
    result = await client.chat([{"role": "user", "content": "只回复 ok"}])
    assert result

