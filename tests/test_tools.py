from typing import Any

import tripartite_agent_surface.northstar_tools as tools


class FakeClient:
    def graph(self) -> dict[str, Any]:
        return {
            "nodes": {
                "req://demo/do-thing": {
                    "type": "CapabilitySpec",
                    "data": {"title": "Do Thing", "lifecycle": "ACTIVE", "tags": ["demo"]},
                }
            },
            "edges": [],
        }

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "node_count": 1, "edge_count": 0}

    def tenants(self) -> dict[str, Any]:
        return {"tenants": [{"tenant_slug": "tripartite"}]}

    def solutions(self) -> dict[str, Any]:
        return {"solutions": [{"solution_name": "demo"}]}

    def openapi(self) -> dict[str, Any]:
        return {"info": {"title": "NorthStar", "version": "test"}, "paths": {"/health": {}}}

    def resolve_uri(self, uri: str, *, default_tenant: str, default_version: str) -> dict[str, Any]:
        return {"canonical_uri": f"req://{default_tenant}:demo/dothing@{default_version}"}

    def governing_context(self, target_uri: str) -> dict[str, Any]:
        return {"target_symbol": target_uri, "capabilities": []}


def test_describe_authority_reports_live_vocabulary(monkeypatch):
    monkeypatch.setattr(tools, "_client", lambda: FakeClient())
    result = tools.describe_authority()
    assert result["status"] == "ok"
    assert result["data"]["live_vocabulary"]["node_types"] == ["CapabilitySpec"]
    assert result["catalog_revision"].startswith("derived-sha256:")


def test_get_nodes_uses_exact_identifiers(monkeypatch):
    monkeypatch.setattr(tools, "_client", lambda: FakeClient())
    result = tools.get_nodes(["req://demo/do", "req://demo/do-thing"])
    assert result["status"] == "partial"
    assert list(result["data"]["nodes"]) == ["req://demo/do-thing"]
    assert result["data"]["missing"] == ["req://demo/do"]


def test_resolve_references_does_not_claim_foreign_resolution(monkeypatch):
    monkeypatch.setattr(tools, "_client", lambda: FakeClient())
    result = tools.resolve_references([
        "req://demo/dothing",
        "csi://demo/service.run",
        "data://logical/demo/Thing",
    ])
    statuses = {item["input"]: item["status"] for item in result["data"]["results"]}
    assert statuses["req://demo/dothing"] == "resolved"
    assert statuses["csi://demo/service.run"] == "not_checked"
    assert statuses["data://logical/demo/Thing"] == "not_checked"
