from datetime import datetime
from uuid import uuid4

from src.domain.entities.message_parts import SystemPromptPart, TextPart, UserPromptPart
from src.domain.entities.thread import Message, MessageRequest, MessageResponse, Thread


class TestThread:
    def test_thread_creation(self):
        thread_id = uuid4()
        title = "Test Thread"
        created_at = datetime.now()
        updated_at = datetime.now()

        thread = Thread(
            id=thread_id, title=title, created_at=created_at, updated_at=updated_at
        )

        assert thread.id == thread_id
        assert thread.title == title
        assert thread.created_at == created_at
        assert thread.updated_at == updated_at
        assert thread.messages is None

    def test_add_message_to_empty_thread(self):
        thread = Thread(
            id=uuid4(),
            title="Test Thread",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        message = Message(id=uuid4(), thread_id=thread.id, created_at=datetime.now())

        original_updated_at = thread.updated_at
        thread.add_message(message)

        assert len(thread.messages) == 1
        assert thread.messages[0] == message
        assert thread.updated_at > original_updated_at

    def test_add_multiple_messages(self):
        thread = Thread(
            id=uuid4(),
            title="Test Thread",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        message1 = Message(id=uuid4(), thread_id=thread.id, created_at=datetime.now())
        message2 = Message(id=uuid4(), thread_id=thread.id, created_at=datetime.now())

        thread.add_message(message1)
        thread.add_message(message2)

        assert len(thread.messages) == 2
        assert thread.messages[0] == message1
        assert thread.messages[1] == message2

    def test_get_last_message_path_empty_thread(self):
        thread = Thread(
            id=uuid4(),
            title="Empty Thread",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        path = thread.get_last_message_path()
        assert path == []

    def test_get_last_message_path_single_message(self):
        thread = Thread(
            id=uuid4(),
            title="Single Message Thread",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        message = Message(id=uuid4(), thread_id=thread.id, created_at=datetime.now())
        thread.add_message(message)

        path = thread.get_last_message_path()
        assert len(path) == 1
        assert path[0] == message

    def test_get_last_message_path_linear_chain(self):
        thread = Thread(
            id=uuid4(),
            title="Linear Chain Thread",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Create a linear chain: root -> child1 -> child2
        base_time = datetime.now()
        root = Message(
            id=uuid4(), thread_id=thread.id, created_at=base_time, parent_id=None
        )

        child1 = Message(
            id=uuid4(),
            thread_id=thread.id,
            created_at=base_time.replace(microsecond=base_time.microsecond + 1000),
            parent_id=root.id,
        )

        child2 = Message(
            id=uuid4(),
            thread_id=thread.id,
            created_at=base_time.replace(microsecond=base_time.microsecond + 2000),
            parent_id=child1.id,
        )

        # Add messages in random order
        thread.add_message(child1)
        thread.add_message(root)
        thread.add_message(child2)

        path = thread.get_last_message_path()
        assert len(path) == 3
        assert path[0] == root
        assert path[1] == child1
        assert path[2] == child2

    def test_get_last_message_path_with_branches(self):
        thread = Thread(
            id=uuid4(),
            title="Branched Thread",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Create a branched structure:
        #     root
        #    /    \
        # child1  child2 (latest)
        base_time = datetime.now()
        root = Message(
            id=uuid4(), thread_id=thread.id, created_at=base_time, parent_id=None
        )

        child1 = Message(
            id=uuid4(),
            thread_id=thread.id,
            created_at=base_time.replace(microsecond=base_time.microsecond + 1000),
            parent_id=root.id,
        )

        child2 = Message(
            id=uuid4(),
            thread_id=thread.id,
            created_at=base_time.replace(microsecond=base_time.microsecond + 2000),
            parent_id=root.id,
        )

        thread.add_message(root)
        thread.add_message(child1)
        thread.add_message(child2)

        path = thread.get_last_message_path()
        assert len(path) == 2
        assert path[0] == root
        assert path[1] == child2  # child2 is the latest

    def test_get_last_message_path_orphaned_message(self):
        thread = Thread(
            id=uuid4(),
            title="Orphaned Message Thread",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Create a message with a parent_id that doesn't exist
        orphaned = Message(
            id=uuid4(),
            thread_id=thread.id,
            created_at=datetime.now(),
            parent_id=uuid4(),  # Non-existent parent
        )

        thread.add_message(orphaned)

        path = thread.get_last_message_path()
        assert len(path) == 1
        assert path[0] == orphaned


class TestMessage:
    def test_message_creation(self):
        message_id = uuid4()
        thread_id = uuid4()
        created_at = datetime.now()
        parent_id = uuid4()

        message = Message(
            id=message_id,
            thread_id=thread_id,
            created_at=created_at,
            parent_id=parent_id,
        )

        assert message.id == message_id
        assert message.thread_id == thread_id
        assert message.created_at == created_at
        assert message.parent_id == parent_id


class TestMessageRequest:
    def test_message_request_creation(self):
        message_id = uuid4()
        thread_id = uuid4()
        created_at = datetime.now()
        instructions = "Test instructions"

        request = MessageRequest(
            id=message_id,
            thread_id=thread_id,
            created_at=created_at,
            instructions=instructions,
        )

        assert request.id == message_id
        assert request.thread_id == thread_id
        assert request.created_at == created_at
        assert request.instructions == instructions
        assert request.parts == []

    def test_to_pydantic_ai_model_request(self):
        request = MessageRequest(
            id=uuid4(),
            thread_id=uuid4(),
            created_at=datetime.now(),
            instructions="Test instructions",
        )

        system_part = SystemPromptPart(
            id=uuid4(),
            order_index=0,
            created_at=datetime.now(),
            content="System prompt",
        )

        user_part = UserPromptPart(
            id=uuid4(), order_index=1, created_at=datetime.now(), content="User message"
        )

        request.parts = [system_part, user_part]

        pydantic_request = request.to_pydantic_ai_model_request()

        assert pydantic_request.instructions == "Test instructions"
        assert pydantic_request.kind == "request"
        assert len(pydantic_request.parts) == 2


class TestMessageResponse:
    def test_message_response_creation(self):
        message_id = uuid4()
        thread_id = uuid4()
        created_at = datetime.now()
        model_name = "test-model"
        usage_tokens = 100

        response = MessageResponse(
            id=message_id,
            thread_id=thread_id,
            created_at=created_at,
            model_name=model_name,
            usage_tokens=usage_tokens,
        )

        assert response.id == message_id
        assert response.thread_id == thread_id
        assert response.created_at == created_at
        assert response.model_name == model_name
        assert response.usage_tokens == usage_tokens
        assert response.parts == []

    def test_to_pydantic_ai_model_response(self):
        response = MessageResponse(
            id=uuid4(),
            thread_id=uuid4(),
            created_at=datetime.now(),
            model_name="test-model",
            usage_tokens=100,
        )

        text_part = TextPart(
            id=uuid4(),
            order_index=0,
            created_at=datetime.now(),
            content="Response text",
        )

        response.parts = [text_part]

        pydantic_response = response.to_pydantic_ai_model_response()

        assert pydantic_response.model_name == "test-model"
        assert pydantic_response.usage.total_tokens == 100
        assert len(pydantic_response.parts) == 1
