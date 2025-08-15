import asyncio
import time

from fastmcp import Client, Context, FastMCP

mcp = FastMCP(name="ContextDemo")


@mcp.tool
async def process_data(ctx: Context) -> dict:
    """Process data from a resource with progress reporting."""

    # Report progress
    await ctx.info("Starting data processing...(0/100)")
    time.sleep(5)  # Simulate some processing time

    # Report progress
    await ctx.info("Starting data processing...(50/100)")
    time.sleep(5)  # Simulate some processing time

    await ctx.info("Data processing completed.")
    return {"state": "completed"}


async def main():
    async with Client(mcp) as client:
        # ツール一覧の取得
        tools = await client.list_tools()
        print(tools)

        # ツール実行
        result = await client.call_tool("process_data")
        # result.content は Message[]。text/JSONのどちらかで返る仕様に合わせて評価
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
