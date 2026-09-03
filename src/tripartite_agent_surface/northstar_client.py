"""Small HTTP client for NorthStar's existing read API."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

import httpx


class NorthstarApiError(RuntimeError):
    """A structured failure returned by or encountered while calling NorthStar."""

    def __init__(
        self,
        message: str,
        *,
        kind: str = "backend_error",
        status_code: int | None = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.kind = kind
        self.status_code = status_code
        self.details = details


@dataclass(frozen=True)
class NorthstarClientConfig:
    base_url: str = "http://127.0.0.1:9480"
    bearer_token: str | None = None
    timeout_seconds: float = 15.0

    @classmethod
    def from_environment(cls) -> "NorthstarClientConfig":
        timeout_raw = os.getenv("NORTHSTAR_TIMEOUT_SECONDS", "15")
        try:
            timeout = float(timeout_raw)
        except ValueError as exc:
            raise ValueError("NORTHSTAR_TIMEOUT_SECONDS must be numeric") from exc
        if timeout <= 0:
            raise ValueError("NORTHSTAR_TIMEOUT_SECONDS must be positive")
        return cls(
            base_url=os.getenv("NORTHSTAR_BASE_URL", cls.base_url).rstrip("/"),
            bearer_token=os.getenv("NORTHSTAR_BEARER_TOKEN") or None,
            timeout_seconds=timeout,
        )


class NorthstarClient:
    """Read-only client. It intentionally exposes no write methods."""

    def __init__(self, config: NorthstarClientConfig | None = None) -> None:
        self.config = config or NorthstarClientConfig.from_environment()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        headers = {"Accept": "application/json"}
        if self.config.bearer_token:
            headers["Authorization"] = f"Bearer {self.config.bearer_token}"
        try:
            with httpx.Client(
                base_url=self.config.base_url,
                timeout=self.config.timeout_seconds,
                headers=headers,
            ) as client:
                response = client.request(method, path, params=params, json=json)
        except httpx.TimeoutException as exc:
            raise NorthstarApiError(str(exc), kind="timeout") from exc
        except httpx.HTTPError as exc:
            raise NorthstarApiError(str(exc), kind="dependency_unavailable") from exc

        if response.status_code >= 400:
            try:
                details: Any = response.json()
            except ValueError:
                details = response.text
            kind = "not_found" if response.status_code == 404 else "backend_rejected"
            raise NorthstarApiError(
                f"NorthStar returned HTTP {response.status_code}",
                kind=kind,
                status_code=response.status_code,
                details=details,
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise NorthstarApiError(
                "NorthStar returned a non-JSON response",
                kind="invalid_backend_response",
                status_code=response.status_code,
            ) from exc
        if not isinstance(payload, dict):
            raise NorthstarApiError(
                "NorthStar returned JSON with an unexpected top-level type",
                kind="invalid_backend_response",
                details={"actual_type": type(payload).__name__},
            )
        return payload

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def tenants(self) -> dict[str, Any]:
        return self._request("GET", "/api/v1/tenants")

    def solutions(self) -> dict[str, Any]:
        return self._request("GET", "/api/v1/solutions")

    def graph(self) -> dict[str, Any]:
        return self._request("GET", "/api/v1/graph")

    def openapi(self) -> dict[str, Any]:
        return self._request("GET", "/openapi.json")

    def resolve_uri(
        self,
        uri: str,
        *,
        default_tenant: str = "tripartite",
        default_version: str = "latest",
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/api/v1/uris/resolve",
            json={
                "uri": uri,
                "default_tenant": default_tenant,
                "default_version": default_version,
            },
        )

    def governing_context(self, target_uri: str) -> dict[str, Any]:
        return self._request(
            "GET",
            "/api/v1/closure",
            params={"target_uri": target_uri},
        )
