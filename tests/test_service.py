import os
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.service.conversation_service import ConversationService


class TestConversationServicePrompts:
    def setup_method(self):
        self.service = ConversationService()
        self.service._load_prompts()

    def test_load_prompts_from_yaml(self):
        assert "system" in self.service.prompts_config
        assert "turns" in self.service.prompts_config
        assert len(self.service.prompts_config["turns"]) == 3

    def test_system_prompt_en(self):
        prompt = self.service.get_system_prompt("en")
        assert "Python" in prompt
        assert len(prompt) > 10

    def test_system_prompt_tr(self):
        prompt = self.service.get_system_prompt("tr")
        assert "Python" in prompt
        assert len(prompt) > 10

    def test_get_turn_prompt_en(self):
        for i in range(1, 4):
            prompt = self.service.get_turn_prompt(i, "en")
            assert len(prompt) > 50

    def test_get_turn_prompt_tr(self):
        for i in range(1, 4):
            prompt = self.service.get_turn_prompt(i, "tr")
            assert len(prompt) > 50

    def test_get_turn_notes_both_langs(self):
        for i in range(1, 4):
            en_notes = self.service.get_turn_notes(i, "en")
            tr_notes = self.service.get_turn_notes(i, "tr")
            assert len(en_notes) > 0
            assert len(tr_notes) > 0

    def test_expected_success(self):
        assert self.service.get_turn_expected_success(1) is True
        assert self.service.get_turn_expected_success(2) is True
        assert self.service.get_turn_expected_success(3) is False

    def test_total_turns(self):
        assert self.service.get_total_turns() == 3

    def test_invalid_turn_number(self):
        with pytest.raises(ValueError):
            self.service.get_turn_prompt(99, "en")


class TestConversationServiceLifecycle:
    @pytest.mark.asyncio
    async def test_start_conversation(self):
        service = ConversationService()
        service._load_prompts()
        service.repository = AsyncMock()
        service.repository.model = "openai/gpt-4o"

        conv = await service.start_conversation("en")
        assert conv is not None
        assert conv.model == "openai/gpt-4o"
        assert len(conv.messages) == 1
        assert conv.messages[0].role.value == "system"

    @pytest.mark.asyncio
    async def test_start_conversation_turkish(self):
        service = ConversationService()
        service._load_prompts()
        service.repository = AsyncMock()
        service.repository.model = "openai/gpt-4o"

        conv = await service.start_conversation("tr")
        system_msg = conv.messages[0].content
        assert "Python" in system_msg

    @pytest.mark.asyncio
    async def test_execute_turn(self):
        service = ConversationService()
        service._load_prompts()
        service.repository = AsyncMock()
        service.repository.model = "openai/gpt-4o"
        service.repository.chat_completion = AsyncMock(return_value="def is_balanced(s): pass")

        await service.start_conversation("en")
        response = await service.execute_turn(1, "en")

        assert response == "def is_balanced(s): pass"
        assert len(service.conversation.messages) == 3  # system + user + assistant
        assert len(service.conversation.turns) == 1
        assert service.conversation.turns[0].success is True

    @pytest.mark.asyncio
    async def test_execute_turn_3_expected_failure(self):
        service = ConversationService()
        service._load_prompts()
        service.repository = AsyncMock()
        service.repository.model = "openai/gpt-4o"
        service.repository.chat_completion = AsyncMock(return_value="class RegexEngine: pass")

        await service.start_conversation("en")
        # Execute turns 1 and 2 first
        await service.execute_turn(1, "en")
        await service.execute_turn(2, "en")
        await service.execute_turn(3, "en")

        assert service.conversation.turns[2].success is False

    @pytest.mark.asyncio
    async def test_execute_turn_without_start_raises(self):
        service = ConversationService()
        service._load_prompts()
        with pytest.raises(RuntimeError, match="No active conversation"):
            await service.execute_turn(1, "en")

    @pytest.mark.asyncio
    async def test_execute_invalid_turn_raises(self):
        service = ConversationService()
        service._load_prompts()
        service.repository = AsyncMock()
        service.repository.model = "openai/gpt-4o"
        await service.start_conversation("en")

        with pytest.raises(ValueError, match="Invalid turn number"):
            await service.execute_turn(5, "en")

    @pytest.mark.asyncio
    async def test_run_all_turns(self):
        service = ConversationService()
        service._load_prompts()
        service.repository = AsyncMock()
        service.repository.model = "openai/gpt-4o"
        service.repository.chat_completion = AsyncMock(return_value="mock response")

        conv = await service.run_all_turns("en")
        assert len(conv.turns) == 3
        assert service.repository.chat_completion.call_count == 3


class TestConversationServiceExport:
    @pytest.mark.asyncio
    async def test_export_json(self, tmp_path):
        service = ConversationService()
        service._load_prompts()
        service.output_dir = str(tmp_path)
        service.repository = AsyncMock()
        service.repository.model = "openai/gpt-4o"
        service.repository.chat_completion = AsyncMock(return_value="mock")

        await service.run_all_turns("en")
        filepath = service.export_json()

        assert os.path.exists(filepath)
        with open(filepath, "r") as f:
            data = json.load(f)
        assert data["model"] == "openai/gpt-4o"
        assert len(data["turns"]) == 3
        assert "metadata" in data
        assert data["metadata"]["assessment"] == "GenAI Conversation Design"

    @pytest.mark.asyncio
    async def test_export_without_conversation_raises(self):
        service = ConversationService()
        with pytest.raises(RuntimeError, match="No conversation to export"):
            service.export_json()
