from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("whattime", port=8001)


@mcp.tool()
async def get_time() -> str:
    """Get the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
