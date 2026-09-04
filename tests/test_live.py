import os

import anyio
import pytest
from mcp.client import Client

from tripartite_agent_surface.server import create_server


@pytest.mark.live
@pytest.mark.skipif(
    os.getenv("RUN_NORTHSTAR_LIVE") != "1", reason="set RUN_NORTHSTAR_LIVE=1"
)
def test_live_northstar_v2_operations_over_mcp():
    async def check() -> None:
        async with Client(create_server(), raise_exceptions=True) as client:
            tools = await client.list_tools()
            assert {tool.name for tool in tools.tools} == {
                "describe_authority",
                "resolve_references",
                "get_nodes",
                "search_nodes",
                "query_graph",
                "find_paths",
                "get_governing_context",
                "compare_revisions",
                "analyze_integrity",
            }
            authority = (
                await client.call_tool("describe_authority", {})
            ).structured_content
            assert authority["status"] == "OK"
            revision = authority["catalog_revision"]["revision_id"]
            assert revision.startswith("nsr-sha256:")
            assert authority["data"]["counts"]["unique_visible_nodes"] > 0

            search = (
                await client.call_tool(
                    "search_nodes",
                    {
                        "revision": revision,
                        "node_types": ["CapabilitySpec"],
                        "solutions": ["northstar"],
                        "page_size": 2,
                    },
                )
            ).structured_content
            candidate = search["data"]["matches"][0]["uri"]
            requests = {
                "resolve_references": {
                    "references": [candidate, "csi://northstar/service.app.create_app"],
                    "revision": revision,
                },
                "get_nodes": {"uris": [candidate], "revision": revision},
                "query_graph": {
                    "start_uris": [candidate],
                    "revision": revision,
                    "page_size": 2,
                },
                "find_paths": {
                    "source_uris": [candidate],
                    "target_uris": ["decision://arch/adr-0002-equal-capability-api"],
                    "revision": revision,
                },
                "get_governing_context": {
                    "target_uris": [candidate],
                    "revision": revision,
                },
                "compare_revisions": {
                    "before_revision": revision,
                    "after_revision": revision,
                },
                "analyze_integrity": {"revision": revision, "page_size": 2},
            }
            for name, arguments in requests.items():
                result = (await client.call_tool(name, arguments)).structured_content
                assert result["status"] in {"OK", "PARTIAL"}
                assert result["operation"].startswith(name + "@")
                assert result["catalog_revision"]["revision_id"] == revision

        assert authority["catalog_revision"]["revision_id"].startswith("nsr-sha256:")

    anyio.run(check)
