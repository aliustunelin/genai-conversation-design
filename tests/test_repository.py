import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.repository.openrouter_repository import OpenRouterRepository


class TestOpenRouterRepository:
    def test_init(self):
        repo = OpenRouterRepository()
        assert repo.api_key is not None
        assert repo.base_url == "https://openrouter.ai/api/v1"
        assert repo.model == "openai/gpt-4o"
        assert repo.client is None

    @pytest.mark.asyncio
    async def test_initialize_creates_client(self):
        repo = OpenRouterRepository()
        await repo.initialize()
        assert repo.client is not None
        await repo.close()

    @pytest.mark.asyncio
    async def test_close_without_init(self):
        repo = OpenRouterRepository()
        await repo.close()  # should not raise

    @pytest.mark.asyncio
    async def test_chat_completion_without_init_raises(self):
        repo = OpenRouterRepository()
        with pytest.raises(RuntimeError, match="Client not initialized"):
            await repo.chat_completion([{"role": "user", "content": "hi"}])

    @pytest.mark.asyncio
    async def test_chat_completion_sends_correct_payload(self):
        repo = OpenRouterRepository()
        repo.client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "hello back"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }
        mock_response.raise_for_status = MagicMock()
        repo.client.post = AsyncMock(return_value=mock_response)

        messages = [{"role": "user", "content": "hello"}]
        result = await repo.chat_completion(messages, temperature=0.5, max_tokens=100)

        assert result == "hello back"
        repo.client.post.assert_called_once()
        call_args = repo.client.post.call_args
        assert call_args[0][0] == "/chat/completions"
        payload = call_args[1]["json"]
        assert payload["model"] == "openai/gpt-4o"
        assert payload["temperature"] == 0.5
        assert payload["max_tokens"] == 100
