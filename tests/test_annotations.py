"""Every tool of this server is a pure reader, and says so: clients use these hints to decide what is safe to auto-approve.
A tool added later without annotations (or with a wrong one) fails here."""
import asyncio

from fastmcp import Client

from kra_mcp import server


def test_every_tool_declares_that_it_is_read_only():
    async def tools():
        async with Client(server.mcp) as c:
            return await c.list_tools()
    ts = asyncio.run(tools())
    assert ts
    for t in ts:
        a = t.annotations
        assert a is not None and a.readOnlyHint is True and a.idempotentHint is True and a.openWorldHint is False, t.name
