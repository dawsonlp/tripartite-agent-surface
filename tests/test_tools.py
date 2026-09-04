from typing import Any

import tripartite_agent_surface.northstar_tools as tools


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def describe_authority(self, tenant: str) -> dict[str, Any]:
        return {
            "status": "OK",
            "authority": "northstar",
            "catalog_revision": {"revision_id": "nsr-sha256:test"},
            "effective_scope": {"tenant": tenant},
            "data": {"supported_operations": list(tools.TOOL_FUNCTIONS)},
        }

    def explore(
        self, tenant: str, action_path: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        self.calls.append((tenant, action_path, payload))
        return {
            "status": "OK",
            "authority": "northstar",
            "catalog_revision": {"revision_id": "nsr-sha256:test"},
            "effective_scope": {"tenant": tenant},
            "normalized_query": payload,
            "data": {"action_path": action_path},
        }


def test_describe_authority_is_native_passthrough(monkeypatch) -> None:
    fake = FakeClient()
    monkeypatch.setattr(tools, "_client", lambda: fake)
    result = tools.describe_authority()
    assert result["status"] == "OK"
    assert result["catalog_revision"]["revision_id"] == "nsr-sha256:test"
    assert len(result["data"]["supported_operations"]) == 9


def test_search_maps_controls_to_native_operation(monkeypatch) -> None:
    fake = FakeClient()
    monkeypatch.setattr(tools, "_client", lambda: fake)
    result = tools.search_nodes(
        "validate",
        node_types=["CapabilitySpec"],
        has_relationships=["SATISFIES"],
        data_fields=["title"],
        page_size=7,
    )
    assert result["status"] == "OK"
    tenant, action, payload = fake.calls[0]
    assert tenant == "tripartite"
    assert action == "nodes:search"
    assert payload["modes"] == ["STRUCTURED", "LEXICAL"]
    assert payload["projection"]["data_fields"] == ["title"]
    assert payload["page"]["size"] == 7


def test_foreign_resolution_is_delegated_to_authority(monkeypatch) -> None:
    fake = FakeClient()
    monkeypatch.setattr(tools, "_client", lambda: fake)
    tools.resolve_references(
        ["csi://demo/service.run", "data://logical/demo/Thing"],
        foreign_resolution="SYNTAX_ONLY",
    )
    _, action, payload = fake.calls[0]
    assert action == "references:resolve"
    assert payload["references"] == [
        "csi://demo/service.run",
        "data://logical/demo/Thing",
    ]
    assert payload["foreign_resolution"] == "SYNTAX_ONLY"


def test_compare_and_integrity_are_exposed(monkeypatch) -> None:
    fake = FakeClient()
    monkeypatch.setattr(tools, "_client", lambda: fake)
    tools.compare_revisions("r1", "r2")
    tools.analyze_integrity(finding_classes=["DANGLING_INTERNAL_REFERENCE"])
    assert [call[1] for call in fake.calls] == [
        "revisions:compare",
        "integrity:analyze",
    ]
