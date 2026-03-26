# GenAI Conversation Design

A FastAPI service that conducts a **3-turn coding conversation with GPT-4o** via OpenRouter API. The conversation demonstrates effective prompt design in early turns and intentionally exposes model limitations in the final turn.

## What It Does

1. **Turn 1 — Balanced Parentheses Checker**: A classic, well-known problem. GPT-4o produces correct, clean code. Demonstrates the ability to write a clear, well-scoped prompt.

2. **Turn 2 — Mathematical Expression Evaluator**: Asks for a Shunting-Yard based evaluator with operator precedence, parentheses, and negative numbers. More complex, but the model handles it correctly. Demonstrates escalating complexity while guiding the model to success.

3. **Turn 3 — Full Regex Engine from Scratch**: Requests a complete regex engine supporting 14 features simultaneously (literals, quantifiers, non-greedy matching, character classes, lookahead, lookbehind, nested groups, anchors, etc.) with 20 verifiable test cases. The model fails because:
   - Variable-length lookbehind is fundamentally hard (even Python's `re` restricts it)
   - Non-greedy quantifiers behave incorrectly in full-string match context
   - Nested groups with alternation and quantifiers create exponential edge cases
   - The model cannot execute its own code to verify correctness

All prompts are available in **English and Turkish**, loaded from a YAML configuration file.

## Architecture

```
app.py (FastAPI + lifespan)
├── src/router/conversation_router.py   — API endpoints
│   └── src/service/conversation_service.py — Business logic, YAML loader, JSON export
│       ├── src/repository/openrouter_repository.py — Async HTTP client (httpx)
│       └── src/model/conversation.py — Pydantic request/response models
├── src/utils/logger.py — Loguru structured logging
└── prompts/turns.yaml — Prompt definitions (EN + TR)
```

| Layer | Responsibility |
|-------|---------------|
| **Model** | Pydantic data models for messages, turns, API request/response schemas |
| **Repository** | OpenRouter API communication via `httpx.AsyncClient` |
| **Service** | Prompt loading from YAML, conversation orchestration, JSON export |
| **Router** | FastAPI endpoints exposing the service |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/conversation/start` | Start a new conversation |
| `POST` | `/conversation/turn` | Execute a single turn (1-3) |
| `POST` | `/conversation/run-all` | Run all 3 turns and export |
| `POST` | `/conversation/export` | Export current conversation to JSON |

### Example Requests

**Start a conversation (Turkish):**
```bash
curl -X POST http://localhost:8000/conversation/start \
  -H "Content-Type: application/json" \
  -d '{"lang": "tr"}'
```

**Run all 3 turns (English):**
```bash
curl -X POST http://localhost:8000/conversation/run-all \
  -H "Content-Type: application/json" \
  -d '{"lang": "en"}'
```

**Execute a specific turn:**
```bash
curl -X POST http://localhost:8000/conversation/turn \
  -H "Content-Type: application/json" \
  -d '{"turn_number": 2, "lang": "en"}'
```

## Setup

### Local

```bash
# Install dependencies
make install

# Run the server
make run

# Run tests
make test
```

### Docker

```bash
# Build and start
docker-compose up --build -d

# Stop
docker-compose down
```

The service runs on `http://localhost:8000`. Interactive API docs are available at `http://localhost:8000/docs`.

## Configuration

Copy `.env.example` to `.env` and set your OpenRouter API key:

```
OPENROUTER_API_KEY=your-key-here
OPENROUTER_MODEL=openai/gpt-4o
```

Prompts are defined in `prompts/turns.yaml`. Each turn has `en` and `tr` versions.

## Output

After running the conversation, the full interaction is exported to `output/conversation.json` containing:
- All messages (system, user, assistant) with timestamps
- Turn results with success/failure status and notes
- Assessment metadata

## Tests

```bash
make test
```

Tests cover:
- Pydantic model creation and serialization
- YAML prompt loading (both languages)
- Conversation lifecycle (start, turn execution, export)
- FastAPI endpoint responses
- Error handling (invalid turns, missing conversation)

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| **FastAPI** | REST API framework |
| **httpx** | Async HTTP client for OpenRouter API |
| **Pydantic** | Data validation and serialization |
| **PyYAML** | Prompt configuration loading |
| **Loguru** | Structured logging with rotation |
| **Docker** | Containerized deployment |
| **pytest** | Unit testing with async support |
