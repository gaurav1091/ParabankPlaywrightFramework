from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ApiResponse:
    status_code: int
    ok: bool
    headers: dict[str, str]
    body_text: str
    json_payload: Any
