#!/usr/bin/env python3
"""Run the local QCAD bridge or inspect one CAD/HAP pair."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
import urllib.request

# Allow ``python tools/cad_bridge.py`` as well as ``python -m tools.cad_bridge``.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from integration.bridge_server import _project_json, serve
from integration.project_pipeline import inspect_project


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    server = sub.add_parser("serve", help="start the loopback HTTP bridge")
    server.add_argument("--host", default="127.0.0.1")
    server.add_argument("--port", type=int, default=8765)
    inspect = sub.add_parser("inspect", help="run the same inspection without HTTP")
    inspect.add_argument("--cad", required=True)
    inspect.add_argument("--hap", required=True)
    inspect.add_argument("--url", default="http://127.0.0.1:8765/v1/inspect")
    inspect.add_argument("--direct", action="store_true", help="call the core directly")
    args = parser.parse_args()

    if args.command == "serve":
        serve(args.host, args.port)
        return 0
    payload = {"cad_path": args.cad, "hap_path": args.hap, "explicit_mapping": {}}
    if args.direct:
        result = {"protocol_version": "1.0", "ok": True, "data": _project_json(inspect_project(args.cad, args.hap))}
    else:
        request = urllib.request.Request(
            args.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
