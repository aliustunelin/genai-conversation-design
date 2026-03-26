from fastapi import APIRouter, HTTPException

from src.model.conversation import (
    StartConversationRequest,
    StartConversationResponse,
    ExecuteTurnRequest,
    ExecuteTurnResponse,
    RunAllRequest,
    RunAllResponse,
    ExportResponse,
)
from src.service.conversation_service import ConversationService
from src.utils.logger import Logger

logger = Logger.setup()

router = APIRouter(prefix="/conversation", tags=["conversation"])

service = ConversationService()


@router.post("/start", response_model=StartConversationResponse)
async def start_conversation(request: StartConversationRequest):
    """Start a new 3-turn conversation with GPT-4o."""
    try:
        conversation = await service.start_conversation(lang=request.lang)
        return StartConversationResponse(
            conversation_id=conversation.id,
            model=conversation.model,
            lang=request.lang,
            message=f"Conversation started. Use /conversation/turn to execute turns 1-{service.get_total_turns()}.",
        )
    except Exception as e:
        logger.error(f"Error starting conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/turn", response_model=ExecuteTurnResponse)
async def execute_turn(request: ExecuteTurnRequest):
    """Execute a single turn in the conversation."""
    try:
        response = await service.execute_turn(
            turn_number=request.turn_number,
            lang=request.lang,
        )
        turn = service.conversation.turns[-1]
        return ExecuteTurnResponse(
            turn_number=turn.turn_number,
            user_prompt=turn.user_prompt,
            assistant_response=turn.assistant_response,
            expected_success=turn.success,
            notes=turn.notes or "",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing turn: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-all", response_model=RunAllResponse)
async def run_all_turns(request: RunAllRequest):
    """Run all 3 turns automatically and export the conversation."""
    try:
        conversation = await service.run_all_turns(lang=request.lang)
        filepath = service.export_json()
        return RunAllResponse(
            conversation_id=conversation.id,
            model=conversation.model,
            total_turns=len(conversation.turns),
            turns=[t.model_dump() for t in conversation.turns],
            export_path=filepath,
        )
    except Exception as e:
        logger.error(f"Error running all turns: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export", response_model=ExportResponse)
async def export_conversation():
    """Export the current conversation to JSON."""
    try:
        filepath = service.export_json()
        conv = service.conversation
        return ExportResponse(
            filepath=filepath,
            conversation_id=conv.id,
            total_messages=len(conv.messages),
            total_turns=len(conv.turns),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
