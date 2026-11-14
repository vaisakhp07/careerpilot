"""Read-only approved-employer adapter, disabled by default.

No general crawler. Avoid calling this on attacker-controlled board IDs. The
source registry is manually approved and controlled by repository maintainers.
"""
import json
import re
from urllib.request import Request, urlopen

BOARD_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,80}$")
MAX_RESPONSE_BYTES = 1_000_000


def fetch_approved_greenhouse_board(board_id: str, *, approved_ids: frozenset[str]) -> list[dict]:
    if board_id not in approved_ids or not BOARD_RE.fullmatch(board_id):
        raise ValueError("Unapproved Greenhouse board ID")
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_id}/jobs"
    # TODO CP-004: deny redirects to other hosts; isolate worker; rate-limit; verify terms.
    req = Request(url, headers={"User-Agent": "CareerPilot/0.1 (approved test adapter)"})
    with urlopen(req, timeout=6) as response:
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("Job response exceeds size limit")
    data = json.loads(raw)
    return data.get("jobs", [])
