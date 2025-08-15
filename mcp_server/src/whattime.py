import logging
from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("whattime")

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)


@mcp.tool()
async def get_time() -> str:
    """Get the current time."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Current time is: {now}")
    return now


if __name__ == "__main__":
    mcp.run()
