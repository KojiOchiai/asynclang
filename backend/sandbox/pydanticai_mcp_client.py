import asyncio
import json

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

server = MCPServerStreamableHTTP("http://localhost:8000/mcp")
agent = Agent("openai:gpt-4o", toolsets=[server])


async def main():
    async with agent:
        result = await agent.run("I am Alice. What time is it?")
        result = await agent.run("Who am I?", message_history=result.all_messages())

    print(json.dumps(json.loads(result.all_messages_json().decode()), indent=4))
    print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
