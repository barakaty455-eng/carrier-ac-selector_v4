from __future__ import annotations

import json
import threading
import urllib.request

from integration.bridge_protocol import InspectRequest, PROTOCOL_VERSION
from integration.bridge_server import BridgeHandler
from http.server import ThreadingHTTPServer


def test_inspect_request_requires_both_sources():
    request = InspectRequest.from_json({"cad_path": "a.dxf", "hap_path": "b.pdf"})
    assert request.cad_path == "a.dxf"
    assert request.explicit_mapping == {}


def test_inspect_request_rejects_missing_source():
    try:
        InspectRequest.from_json({"cad_path": "a.dxf"})
    except ValueError as exc:
        assert "hap_path" in str(exc)
    else:
        raise AssertionError("missing hap_path should be rejected")


def test_health_endpoint_uses_versioned_envelope():
    server = ThreadingHTTPServer(("127.0.0.1", 0), BridgeHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/health") as response:
            payload = json.load(response)
        assert payload["protocol_version"] == PROTOCOL_VERSION
        assert payload["ok"] is True
        assert payload["data"]["status"] == "ready"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
