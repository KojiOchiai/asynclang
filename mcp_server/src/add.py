# server.py
import logging

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

# サーバー作成
mcp = FastMCP("Demo Server")


# ツール登録
@mcp.tool()
def add(a: int, b: int) -> int:
    """2つの数を加算して返す"""
    logger.info(f"Adding {a} and {b}")
    return a + b


# 手動起動用（mcp run でも起動可能）
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
