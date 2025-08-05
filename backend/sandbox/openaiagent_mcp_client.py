import asyncio

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp


async def whattime_mcp():
    async with MCPServerStreamableHttp(
        params={"url": "http://localhost:8000/mcp"},
    ) as server:
        tools = await server.list_tools()
        print(f"Available tools: {tools}")
        agent = Agent(
            name="Assistant",
            model="gpt-4o",
            mcp_servers=[server],
        )
        # first run
        print("\nFirst run:")
        result = await Runner.run(agent, "I am Alice. What time is it?")
        for part in result.to_input_list():
            print(part, end="\n\n")
        print(result.to_input_list()[2]["output"])
        # second run
        print("\nSecond run:")
        new_input = result.to_input_list() + [{"role": "user", "content": "Who am I?"}]
        result = await Runner.run(agent, new_input)
        for part in result.to_input_list():
            print(part, end="\n\n")


if __name__ == "__main__":
    asyncio.run(whattime_mcp())
    print("MCP server stopped.")
