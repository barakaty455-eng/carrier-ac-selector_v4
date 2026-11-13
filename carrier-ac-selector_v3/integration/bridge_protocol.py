"""JSON contract for the local QCAD <-> Carrier AC Selector bridge."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


PROTOCOL_VERSION = "1.0"


@dataclass(frozen=True)
class InspectRequest:
    cad_path: str
    hap_path: str
    explicit_mapping: dict[str, str]

    @classmethod
    def from_json(cls, payload: Mapping[str, Any]) -> "InspectRequest":
        cad_path = str(payload.get("cad_path", "")).strip()
        hap_path = str(payload.get("hap_path", "")).strip()
        if not cad_path or not hap_path:
            raise ValueError("cad_path and hap_path are required")
        raw_mapping = payload.get("explicit_mapping", {})
        if raw_mapping is None:
            raw_mapping = {}
        if not isinstance(raw_mapping, Mapping):
            raise ValueError("explicit_mapping must be an object")
        mapping = {str(key): str(value) for key, value in raw_mapping.items()}
        return cls(cad_path, hap_path, mapping)


def success(data: Any) -> dict[str, Any]:
    return {"protocol_version": PROTOCOL_VERSION, "ok": True, "data": data}


def failure(message: str) -> dict[str, Any]:
    return {"protocol_version": PROTOCOL_VERSION, "ok": False, "error": message}
