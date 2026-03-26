from src.model.conversation import (
    Message,
    MessageRole,
    Conversation,
    ConversationExport,
    TurnResult,
    StartConversationRequest,
    ExecuteTurnRequest,
    RunAllRequest,
)


class TestMessageRole:
    def test_roles_exist(self):
        assert MessageRole.SYSTEM == "system"
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"


class TestMessage:
    def test_create_message(self):
        msg = Message(role=MessageRole.USER, content="hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "hello"
        assert msg.timestamp is not None

    def test_message_with_all_roles(self):
        for role in MessageRole:
            msg = Message(role=role, content="test")
            assert msg.role == role


class TestConversation:
    def test_create_conversation(self):
        conv = Conversation(model="openai/gpt-4o")
        assert conv.model == "openai/gpt-4o"
        assert conv.messages == []
        assert conv.turns == []
        assert conv.id is not None

    def test_add_message(self):
        conv = Conversation(model="openai/gpt-4o")
        msg = conv.add_message(MessageRole.USER, "hello")
        assert len(conv.messages) == 1
        assert msg.content == "hello"
        assert msg.role == MessageRole.USER

    def test_add_multiple_messages(self):
        conv = Conversation(model="openai/gpt-4o")
        conv.add_message(MessageRole.SYSTEM, "system prompt")
        conv.add_message(MessageRole.USER, "user input")
        conv.add_message(MessageRole.ASSISTANT, "assistant reply")
        assert len(conv.messages) == 3

    def test_get_api_messages(self):
        conv = Conversation(model="openai/gpt-4o")
        conv.add_message(MessageRole.SYSTEM, "be helpful")
        conv.add_message(MessageRole.USER, "hello")
        api_msgs = conv.get_api_messages()
        assert api_msgs == [
            {"role": "system", "content": "be helpful"},
            {"role": "user", "content": "hello"},
        ]

    def test_add_turn(self):
        conv = Conversation(model="openai/gpt-4o")
        conv.add_turn(1, "prompt", "response", True, "note")
        assert len(conv.turns) == 1
        assert conv.turns[0].turn_number == 1
        assert conv.turns[0].success is True
        assert conv.turns[0].notes == "note"


class TestTurnResult:
    def test_create_turn_result(self):
        turn = TurnResult(
            turn_number=1,
            user_prompt="test prompt",
            assistant_response="test response",
            success=True,
            notes="test note",
        )
        assert turn.turn_number == 1
        assert turn.success is True

    def test_turn_result_without_notes(self):
        turn = TurnResult(
            turn_number=2,
            user_prompt="prompt",
            assistant_response="response",
            success=False,
        )
        assert turn.notes is None


class TestConversationExport:
    def test_from_conversation(self):
        conv = Conversation(model="openai/gpt-4o")
        conv.add_message(MessageRole.SYSTEM, "system")
        conv.add_message(MessageRole.USER, "hello")
        conv.add_turn(1, "hello", "hi", True)
        export = ConversationExport.from_conversation(conv, {"key": "value"})
        assert export.id == conv.id
        assert export.model == "openai/gpt-4o"
        assert len(export.messages) == 2
        assert len(export.turns) == 1
        assert export.metadata["key"] == "value"

    def test_export_to_dict(self):
        conv = Conversation(model="openai/gpt-4o")
        conv.add_message(MessageRole.USER, "test")
        export = ConversationExport.from_conversation(conv)
        d = export.model_dump()
        assert "id" in d
        assert "model" in d
        assert "messages" in d
        assert "metadata" in d


class TestRequestModels:
    def test_start_request_defaults(self):
        req = StartConversationRequest()
        assert req.lang == "en"

    def test_start_request_turkish(self):
        req = StartConversationRequest(lang="tr")
        assert req.lang == "tr"

    def test_execute_turn_request(self):
        req = ExecuteTurnRequest(turn_number=2, lang="tr")
        assert req.turn_number == 2
        assert req.lang == "tr"

    def test_run_all_request_defaults(self):
        req = RunAllRequest()
        assert req.lang == "en"
