# event_scheduler_mcp.py
import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("EventScheduler")
_EVENTS = {}


def parse_when(when_iso: str, tz: Optional[str]) -> datetime:
    s = when_iso.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(tz) if tz else timezone.utc)
    return dt.astimezone(timezone.utc)


async def fire_event(ev_id: str, name: str, when_utc: datetime):
    delay = (when_utc - datetime.now(timezone.utc)).total_seconds()
    print(
        f"[{datetime.now(timezone.utc).isoformat()}] Scheduling event '{name}' ({ev_id}) in {delay} seconds"
    )
    if delay > 0:
        await asyncio.sleep(delay)
    print(f"[{datetime.now(timezone.utc).isoformat()}] EVENT FIRED: {name} ({ev_id})")


@mcp.tool()
async def schedule_at(name: str, when_iso: str, tz: Optional[str] = None) -> dict:
    try:
        when_utc = parse_when(when_iso, tz)
    except Exception as e:
        return {"ok": False, "error": str(e)}
    ev_id = str(uuid.uuid4())
    _EVENTS[ev_id] = {"name": name, "when": when_utc}
    logging.info(datetime.now(timezone.utc))
    asyncio.create_task(fire_event(ev_id, name, when_utc))
    return {"ok": True, "id": ev_id, "scheduled_for_utc": when_utc.isoformat()}


if __name__ == "__main__":
    mcp.run(transport="stdio")
