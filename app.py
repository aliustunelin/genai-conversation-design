import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from src.model.conversation import HealthResponse
from src.router.conversation_router import router as conversation_router, service
from src.utils.logger import Logger

load_dotenv()

logger = Logger.setup()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting GenAI Conversation Design service...")
    await service.initialize()
    logger.info("Service ready")
    yield
    logger.info("Shutting down...")
    await service.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title="GenAI Conversation Design",
    description="3-turn coding conversation with GPT-4o to demonstrate prompt design and model limitations.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(conversation_router)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="genai-conversation-design",
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o"),
    )


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("app:app", host=host, port=port, reload=True)
