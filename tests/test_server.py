import anyio
import json
from pathlib import Path
import sys
from mcp import StdioServerParameters
from mcp.client import Client

from tripartite_agent_surface.server import create_app, create_server


def test_server_exposes_only_read_tools():
    async def check() -> None:
        async with Client(create_server(), raise_exceptions=True) as client:
            result = await client.list_tools()
        assert {tool.name for tool in result.tools} == {
            "describe_authority",
            "resolve_references",
            "get_nodes",
            "search_nodes",
            "query_graph",
            "find_paths",
            "get_governing_context",
        }
        for tool in result.tools:
            assert tool.annotations.read_only_hint is True
            assert tool.annotations.destructive_hint is False
            assert tool.output_schema is not None

    anyio.run(check)


def test_streamable_http_app_builds():
    assert create_app() is not None


def test_stdio_subprocess_tool_discovery():
    async def check() -> None:
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "tripartite_agent_surface.server", "stdio"],
        )
        async with Client(parameters, raise_exceptions=True) as client:
            result = await client.list_tools()
        assert "query_graph" in {tool.name for tool in result.tools}

    anyio.run(check)


def test_plugin_mcp_command_discovers_tools():
    async def check() -> None:
        plugin_root = Path(__file__).resolve().parents[1]
        config = json.loads((plugin_root / ".mcp.json").read_text())
        server = config["mcpServers"]["northstar"]
        parameters = StdioServerParameters(
            command=server["command"],
            args=server["args"],
            cwd=plugin_root,
        )
        async with Client(parameters, raise_exceptions=True) as client:
            result = await client.list_tools()
        assert "describe_authority" in {tool.name for tool in result.tools}

    anyio.run(check)
