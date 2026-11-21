"""Greenhouse approved-employer adapter; disabled by default.

Only requests the fixed Greenhouse HTTPS origin. Board IDs must be explicitly
maintainer-approved; external URLs and HTTP redirects are never followed.
"""

import http.client
import json
import re

BOARD_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,80}$")
GREENHOUSE_HOST = "boards-api.greenhouse.io"
MAX_RESPONSE_BYTES = 1_000_000


def fetch_approved_greenhouse_board(
    board_id: str, *, approved_ids: frozenset[str]
) -> list[dict]:
    if board_id not in approved_ids or not BOARD_RE.fullmatch(board_id):
        raise ValueError("Unapproved Greenhouse board ID")

    # HTTPSConnection uses verified TLS by default, connects directly to the
    # fixed host, and never automatically follows 3xx redirects.
    conn = http.client.HTTPSConnection(GREENHOUSE_HOST, timeout=6)
    try:
        conn.request(
            "GET",
            f"/v1/boards/{board_id}/jobs",
            headers={"User-Agent": "CareerPilot/0.1 (approved test adapter)",
                     "Accept": "application/json"},
        )
        response = conn.getresponse()
        if response.status != 200:
            raise ValueError(f"Greenhouse request failed: HTTP {response.status}")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    finally:
        conn.close()

    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("Job response exceeds size limit")
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise ValueError("Unexpected Greenhouse response shape")  # noqa: TRY004 - External API schema validation
    if not all(isinstance(job, dict) for job in data["jobs"]):
        raise ValueError("Unexpected job record shape")
    return data["jobs"]
