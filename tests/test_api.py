import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app import app
from src.router.conversation_router import service


@pytest.fixture
def mock_service():
    service._load_prompts()
    service.repository = AsyncMock()
    service.repository.model = "openai/gpt-4o"
    service.repository.chat_completion = AsyncMock(return_value="mock response code")
    service.repository.initialize = AsyncMock()
    service.repository.close = AsyncMock()
    return service


@pytest.fixture
async def client(mock_service):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "genai-conversation-design"


class TestConversationEndpoints:
    @pytest.mark.asyncio
    async def test_start_conversation_en(self, client, mock_service):
        response = await client.post("/conversation/start", json={"lang": "en"})
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert data["model"] == "openai/gpt-4o"
        assert data["lang"] == "en"

    @pytest.mark.asyncio
    async def test_start_conversation_tr(self, client, mock_service):
        response = await client.post("/conversation/start", json={"lang": "tr"})
        assert response.status_code == 200
        data = response.json()
        assert data["lang"] == "tr"

    @pytest.mark.asyncio
    async def test_execute_turn(self, client, mock_service):
        await client.post("/conversation/start", json={"lang": "en"})
        response = await client.post("/conversation/turn", json={"turn_number": 1, "lang": "en"})
        assert response.status_code == 200
        data = response.json()
        assert data["turn_number"] == 1
        assert data["assistant_response"] == "mock response code"
        assert data["expected_success"] is True

    @pytest.mark.asyncio
    async def test_execute_turn_without_start(self, client):
        mock_service_obj = service
        mock_service_obj.conversation = None
        response = await client.post("/conversation/turn", json={"turn_number": 1, "lang": "en"})
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_run_all(self, client, mock_service):
        response = await client.post("/conversation/run-all", json={"lang": "en"})
        assert response.status_code == 200
        data = response.json()
        assert data["total_turns"] == 3
        assert len(data["turns"]) == 3
        assert "export_path" in data

    @pytest.mark.asyncio
    async def test_export_after_run(self, client, mock_service):
        await client.post("/conversation/run-all", json={"lang": "en"})
        response = await client.post("/conversation/export")
        assert response.status_code == 200
        data = response.json()
        assert "filepath" in data
        assert data["total_turns"] == 3
