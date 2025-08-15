from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

mcp = FastMCP("Notifier")

# セッションごとに送信タスクを保持
_sessions_tasks: dict[ServerSession, asyncio.Task] = {}


async def _send_loop(session: ServerSession, name: str) -> None:
    """5秒おきに通知を送り続ける"""
    counter = 0
    try:
        while True:
            counter += 1
            await session.send_log_message(
                level="info",
                logger="notifier",
                data={
                    "type": "periodic_notification",
                    "name": name,
                    "count": counter,
                    "time_utc": datetime.now(timezone.utc).isoformat(),
                },
            )
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        await session.send_log_message(
            level="info",
            logger="notifier",
            data={"type": "stopped", "name": name},
        )
        raise


@mcp.tool()
async def start_notifying(
    ctx: Context[ServerSession, None], name: str = "default_notification"
) -> dict:
    """
    このツールを呼び出すと、5秒おきに通知を送り続けます。
    - name: 通知に含める名前
    """
    # 既に同セッションでタスクが動いていたら止める
    if ctx.session in _sessions_tasks:
        _sessions_tasks[ctx.session].cancel()

    task = asyncio.create_task(_send_loop(ctx.session, name))
    _sessions_tasks[ctx.session] = task
    await ctx.info(f"Started notifying every 5 seconds with name='{name}'")
    return {"ok": True}


@mcp.tool()
async def stop_notifying(ctx: Context[ServerSession, None]) -> dict:
    """通知ループを停止します"""
    task = _sessions_tasks.pop(ctx.session, None)
    if task:
        task.cancel()
        return {"ok": True}
    return {"ok": False, "error": "no_task"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
