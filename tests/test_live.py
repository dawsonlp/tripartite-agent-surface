import os

import anyio
import pytest
from mcp.client import Client

from tripartite_agent_surface.server import create_server


@pytest.mark.live
@pytest.mark.skipif(os.getenv("RUN_NORTHSTAR_LIVE") != "1", reason="set RUN_NORTHSTAR_LIVE=1")
def test_live_northstar_discovery_over_mcp():
    async def check() -> None:
        async with Client(create_server(), raise_exceptions=True) as client:
            tools = await client.list_tools()
            result = await client.call_tool("describe_authority", {})
        assert "describe_authority" in {tool.name for tool in tools.tools}
        assert result.structured_content["status"] == "ok"
        assert result.structured_content["data"]["counts"]["nodes"] > 0

    anyio.run(check)
