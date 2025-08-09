import asyncio
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.messages import ModelMessagesTypeAdapter

server = MCPServerStreamableHTTP("http://localhost:8000/mcp")
agent = Agent(
    "openai:gpt-4o",
    system_prompt="You are a helpful assistant. Return message with three ! marks.",
    toolsets=[server],
)


async def main():
    message_count = 0
    async with agent.run_stream("I am Alice. What time is it?") as result:
        print(result.all_messages()[message_count + 1 :])
        async for message in result.stream_text():
            print(f"\r{message}", end="", flush=True)
    message_count = len(result.all_messages())
    print("")

    # Save the message history to a file
    history_bytes = ModelMessagesTypeAdapter.dump_json(result.all_messages(), indent=2)
    Path("message_history.json").write_bytes(history_bytes)

    # Load the message history from the file
    row = Path("message_history.json").read_bytes()
    history = ModelMessagesTypeAdapter.validate_json(row)

    # Run the agent with the loaded message history
    async with agent.run_stream("Who am I", message_history=history) as result:
        print(result.all_messages()[message_count + 1 :])
        async for message in result.stream_text():
            print(f"\r{message}", end="", flush=True)
    message_count = len(result.all_messages())
    print("")

    # Print the results
    for message in result.all_messages():
        print(f"\nkind: {message.kind}")
        for part in message.parts:
            if hasattr(part, "content"):
                print(f"{part.part_kind}: {part.content}")
            if part.part_kind == "tool-call":
                print(f"{part.part_kind}: {part.tool_name}: {part.args}")


if __name__ == "__main__":
    asyncio.run(main())
