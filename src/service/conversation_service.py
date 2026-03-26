import os
import json
from typing import Optional

import yaml

from src.model.conversation import (
    Conversation,
    ConversationExport,
    MessageRole,
)
from src.repository.openrouter_repository import OpenRouterRepository
from src.utils.logger import Logger

logger = Logger.setup()


class ConversationService:
    def __init__(self):
        self.repository = OpenRouterRepository()
        self.conversation: Optional[Conversation] = None
        self.prompts_config: dict = {}
        self.output_dir = os.getenv("OUTPUT_DIR", "output")
        self.prompts_path = os.getenv("PROMPTS_PATH", "prompts/turns.yaml")

    async def initialize(self):
        await self.repository.initialize()
        self._load_prompts()
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("ConversationService initialized")

    async def close(self):
        await self.repository.close()
        logger.info("ConversationService closed")

    def _load_prompts(self):
        with open(self.prompts_path, "r", encoding="utf-8") as f:
            self.prompts_config = yaml.safe_load(f)
        turn_count = len(self.prompts_config.get("turns", []))
        logger.info(f"Loaded {turn_count} turns from {self.prompts_path}")

    def get_turn_prompt(self, turn_number: int, lang: str = "en") -> str:
        turns = self.prompts_config.get("turns", [])
        for turn in turns:
            if turn["number"] == turn_number:
                return turn["prompt"][lang]
        raise ValueError(f"Turn {turn_number} not found in prompts config")

    def get_system_prompt(self, lang: str = "en") -> str:
        return self.prompts_config["system"][lang]

    def get_turn_notes(self, turn_number: int, lang: str = "en") -> str:
        turns = self.prompts_config.get("turns", [])
        for turn in turns:
            if turn["number"] == turn_number:
                return turn["notes"][lang]
        return ""

    def get_turn_expected_success(self, turn_number: int) -> bool:
        turns = self.prompts_config.get("turns", [])
        for turn in turns:
            if turn["number"] == turn_number:
                return turn["expected_success"]
        return True

    def get_total_turns(self) -> int:
        return len(self.prompts_config.get("turns", []))

    async def start_conversation(self, lang: str = "en") -> Conversation:
        model = self.repository.model
        self.conversation = Conversation(model=model)
        system_msg = self.get_system_prompt(lang)
        self.conversation.add_message(MessageRole.SYSTEM, system_msg)
        logger.info(f"Conversation started | id: {self.conversation.id} | lang: {lang}")
        return self.conversation

    async def execute_turn(self, turn_number: int, lang: str = "en") -> str:
        if not self.conversation:
            raise RuntimeError("No active conversation. Call start_conversation() first.")

        total = self.get_total_turns()
        if turn_number < 1 or turn_number > total:
            raise ValueError(f"Invalid turn number: {turn_number}. Must be 1-{total}")

        prompt = self.get_turn_prompt(turn_number, lang)
        self.conversation.add_message(MessageRole.USER, prompt)

        logger.info(f"Executing turn {turn_number}/{total} | lang: {lang}")
        response = await self.repository.chat_completion(
            messages=self.conversation.get_api_messages(),
            temperature=0.7,
            max_tokens=4096,
        )

        self.conversation.add_message(MessageRole.ASSISTANT, response)

        expected_success = self.get_turn_expected_success(turn_number)
        notes = self.get_turn_notes(turn_number, lang)
        self.conversation.add_turn(
            turn_number=turn_number,
            user_prompt=prompt,
            assistant_response=response,
            success=expected_success,
            notes=notes,
        )

        logger.info(f"Turn {turn_number} completed | expected_success: {expected_success}")
        return response

    async def run_all_turns(self, lang: str = "en") -> Conversation:
        await self.start_conversation(lang)
        total = self.get_total_turns()
        for turn in range(1, total + 1):
            await self.execute_turn(turn, lang)
        logger.info(f"All {total} turns completed")
        return self.conversation

    def export_json(self, metadata: dict = None) -> str:
        if not self.conversation:
            raise RuntimeError("No conversation to export")

        default_metadata = {
            "assessment": "GenAI Conversation Design",
            "task": "3-turn coding conversation with GPT-4o via OpenRouter",
            "strategy": "Escalating complexity: bracket matching -> expression evaluator -> regex engine",
            "model_limitation_targeted": (
                "Complex multi-feature implementation with edge cases "
                "(regex engine with lookahead/lookbehind + non-greedy + nested groups)"
            ),
        }
        if metadata:
            default_metadata.update(metadata)

        export = ConversationExport.from_conversation(self.conversation, default_metadata)
        export_dict = export.model_dump()

        filepath = os.path.join(self.output_dir, "conversation.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Conversation exported to {filepath}")
        return filepath
