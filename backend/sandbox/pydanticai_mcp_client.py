import asyncio
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.messages import ModelMessagesTypeAdapter
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

server = MCPServerStreamableHTTP("http://localhost:8000/mcp")
agent = Agent(
    "openai:gpt-4o",
    system_prompt="You are a helpful assistant. Return message with three ! marks.",
    toolsets=[server],
)

model = OpenAIResponsesModel("o3")
settings = OpenAIResponsesModelSettings(
    openai_reasoning_effort="low", openai_reasoning_summary="detailed"
)
agent = Agent(
    model,
    system_prompt="You are a helpful assistant. Return message with three ! marks.",
    model_settings=settings,
    toolsets=[server],
)


async def run_agent(agent: Agent, prompt: str, message_history: list):
    async with agent.run_stream(prompt, message_history=message_history) as result:
        print(result.new_messages_json())
        async for message in result.stream_text():
            print(f"\r{message}", end="", flush=True)
    print("")
    print(result.new_messages())
    return result


async def main():
    result = await run_agent(agent, "I am Alice. What time is it?", [])

    # Save the message history to a file
    history_bytes = ModelMessagesTypeAdapter.dump_json(result.all_messages(), indent=2)
    Path("message_history.json").write_bytes(history_bytes)

    # Load the message history from the file
    row = Path("message_history.json").read_bytes()
    history = ModelMessagesTypeAdapter.validate_json(row)

    # Run the agent with the loaded message history
    result = await run_agent(agent, "Who am I", history)

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
