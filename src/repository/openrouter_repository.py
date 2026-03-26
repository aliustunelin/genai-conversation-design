import os
import httpx
from typing import List, Dict, Any, Optional

from src.utils.logger import Logger

logger = Logger.setup()


class OpenRouterRepository:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")
        self.client: Optional[httpx.AsyncClient] = None

    async def initialize(self):
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/genai-assessment",
                "X-Title": "GenAI Conversation Design Assessment",
            },
            timeout=120.0,
        )
        logger.info(f"OpenRouter client initialized | model: {self.model}")

    async def close(self):
        if self.client:
            await self.client.aclose()
            logger.info("OpenRouter client closed")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        if not self.client:
            raise RuntimeError("Client not initialized. Call initialize() first.")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        logger.info(f"Sending request to OpenRouter | messages: {len(messages)} | model: {self.model}")

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        usage = data.get("usage", {})
        logger.info(
            f"Response received | "
            f"prompt_tokens: {usage.get('prompt_tokens', 'N/A')} | "
            f"completion_tokens: {usage.get('completion_tokens', 'N/A')}"
        )

        return content
