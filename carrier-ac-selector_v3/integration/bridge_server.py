"""Local, loopback-only HTTP bridge for QCAD and the engineering core."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .bridge_protocol import InspectRequest, failure, success
from .project_pipeline import inspect_project


def _space_json(space: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in ("room_id", "label", "name", "area", "perimeter", "layer", "effective_layer"):
        if hasattr(space, name):
            value = getattr(space, name)
            result[name] = value if isinstance(value, (str, int, float, bool, type(None))) else str(value)
    # Keep a stable display name for clients while preserving the detector's
    # original ``label`` field and its exact source spelling.
    if "name" not in result and "label" in result:
        result["name"] = result["label"]
    if not result:
        result["value"] = str(space)
    return result


def _project_json(project: Any) -> dict[str, Any]:
    return {
        "cad_path": str(project.cad_path),
        "hap_path": str(project.hap_path),
        "units": project.cad_document.units,
        "units_verified": project.cad_document.units_verified,
        "spaces": [_space_json(space) for space in project.spaces],
        "hap_systems": [
            {
                "name": item.name,
                "cooling_load_btu": item.cooling_load_btu,
                "airflow_cfm": item.airflow_cfm,
                "sensible_load_btu": item.sensible_load_btu,
                "warnings": list(item.warnings),
            }
            for item in project.hap_systems
        ],
        "matches": [vars(item) for item in project.matches],
        "diagnostics": list(project.diagnostics),
    }


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "CarrierACBridge/1.0"

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(200, success({"service": "carrier-ac-selector", "status": "ready"}))
        else:
            self._send(404, failure("Unknown endpoint"))

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/inspect":
            self._send(404, failure("Unknown endpoint"))
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            request = InspectRequest.from_json(payload)
            project = inspect_project(
                request.cad_path,
                request.hap_path,
                explicit_mapping=request.explicit_mapping,
            )
            self._send(200, success(_project_json(project)))
        except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
            self._send(400, failure(str(exc)))
        except Exception as exc:  # keep the bridge process alive for the next request
            self._send(500, failure(f"Bridge inspection failed: {exc}"))

    def log_message(self, format: str, *args: Any) -> None:
        print("[carrier-bridge] " + format % args)


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Serve only on loopback; this endpoint is not intended for network exposure."""
    server = ThreadingHTTPServer((host, port), BridgeHandler)
    print(f"Carrier bridge listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
