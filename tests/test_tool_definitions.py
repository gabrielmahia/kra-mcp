"""Tool definitions are what an AI client reads before it chooses a tool; Glama scores them (the server score is 60% mean + 40% worst tool).
Every tool needs a real description (purpose, when to use, what it returns, limits) and every parameter needs a description."""
import asyncio

from fastmcp import Client

from kra_mcp import server


def _tools():
    async def go():
        async with Client(server.mcp) as c:
            return await c.list_tools()
    return asyncio.run(go())


def test_every_tool_description_says_when_to_use_it_and_what_it_does_to_the_world():
    for t in _tools():
        d = t.description or ""
        assert len(d) >= 200, (t.name, len(d))
        assert "Use when" in d or "Use this" in d or "Takes no arguments" in d, t.name
        assert "Read-only" in d or "read-only" in d, t.name


def test_every_parameter_has_a_description():
    for t in _tools():
        for name, prop in (t.inputSchema.get("properties") or {}).items():
            assert prop.get("description"), (t.name, name)
