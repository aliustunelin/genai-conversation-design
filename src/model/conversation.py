from enum import Enum
from typing import List, Optional, Literal
from datetime import datetime

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class TurnResult(BaseModel):
    turn_number: int
    user_prompt: str
    assistant_response: str
    success: bool
    notes: Optional[str] = None


class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    model: str
    messages: List[Message] = Field(default_factory=list)
    turns: List[TurnResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    def add_message(self, role: MessageRole, content: str) -> Message:
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        return msg

    def get_api_messages(self) -> list[dict]:
        return [{"role": m.role.value, "content": m.content} for m in self.messages]

    def add_turn(self, turn_number: int, user_prompt: str, assistant_response: str, success: bool, notes: str = None):
        self.turns.append(TurnResult(
            turn_number=turn_number,
            user_prompt=user_prompt,
            assistant_response=assistant_response,
            success=success,
            notes=notes,
        ))


class ConversationExport(BaseModel):
    id: str
    model: str
    created_at: str
    messages: list[dict]
    turns: list[dict]
    metadata: dict = Field(default_factory=dict)

    @classmethod
    def from_conversation(cls, conv: Conversation, metadata: dict = None) -> "ConversationExport":
        return cls(
            id=conv.id,
            model=conv.model,
            created_at=conv.created_at.isoformat(),
            messages=[
                {
                    "role": m.role.value,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in conv.messages
            ],
            turns=[t.model_dump() for t in conv.turns],
            metadata=metadata or {},
        )


# --- FastAPI Request/Response models ---

class StartConversationRequest(BaseModel):
    lang: Literal["en", "tr"] = "en"


class StartConversationResponse(BaseModel):
    conversation_id: str
    model: str
    lang: str
    message: str


class ExecuteTurnRequest(BaseModel):
    turn_number: int = Field(ge=1, le=3)
    lang: Literal["en", "tr"] = "en"


class ExecuteTurnResponse(BaseModel):
    turn_number: int
    user_prompt: str
    assistant_response: str
    expected_success: bool
    notes: str


class RunAllRequest(BaseModel):
    lang: Literal["en", "tr"] = "en"


class RunAllResponse(BaseModel):
    conversation_id: str
    model: str
    total_turns: int
    turns: list[dict]
    export_path: str


class ExportResponse(BaseModel):
    filepath: str
    conversation_id: str
    total_messages: int
    total_turns: int


class HealthResponse(BaseModel):
    status: str
    service: str
    model: str
