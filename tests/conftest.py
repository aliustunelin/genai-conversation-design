import os
import pytest

os.environ["OPENROUTER_API_KEY"] = "test-key"
os.environ["OPENROUTER_BASE_URL"] = "https://openrouter.ai/api/v1"
os.environ["OPENROUTER_MODEL"] = "openai/gpt-4o"
os.environ["OUTPUT_DIR"] = "output"
os.environ["PROMPTS_PATH"] = "prompts/turns.yaml"
