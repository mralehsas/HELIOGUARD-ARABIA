#!/usr/bin/env python3
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = "https://kauai.ccmc.gsfc.nasa.gov/CMEscoreboard/WS/get/predictions"
UA = "HELIOGUARD-ARABIA/1.0 (+GitHub Actions CCMC gateway)"


def fetch(days: int, closed_only: bool, skip_no_arrival: bool, out: str) -> int:
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=days)).date().isoformat()
    end = now.date().isoformat()
    query = urllib.parse.urlencode({
        "CMEtimeStart": start,
        "CMEtimeEnd": end,
        "skipNoArrivalObservedCMEs": str(skip_no_arrival).lower(),
        "closeOutCMEsOnly": str(closed_only).lower(),
    })
    url = BASE + "?" + query
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as response:
        events = json.load(response)
        if not isinstance(events, list):
            raise RuntimeError(f"Unexpected CCMC payload: {type(events).__name__}")
    payload = {
        "schema": "HELIOGUARD_CCMC_GATEWAY_V1",
        "fetchedAt": now.isoformat().replace("+00:00", "Z"),
        "source": BASE,
        "query": {
            "CMEtimeStart": start,
            "CMEtimeEnd": end,
            "skipNoArrivalObservedCMEs": skip_no_arrival,
            "closeOutCMEsOnly": closed_only,
        },
        "events": events,
    }
    path = Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{out}: {len(events)} events")
    return len(events)


def validate(path: str) -> None:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    assert payload.get("schema") == "HELIOGUARD_CCMC_GATEWAY_V1"
    assert isinstance(payload.get("events"), list)
    assert payload.get("fetchedAt")
    assert payload.get("source") == BASE


def main() -> None:
    fetch(45, False, False, "data/ccmc-scoreboard-recent.json")
    fetch(90, True, False, "data/ccmc-scoreboard-90d.json")
    validate("data/ccmc-scoreboard-recent.json")
    validate("data/ccmc-scoreboard-90d.json")
    print("CCMC gateway cache: VALID")


if __name__ == "__main__":
    main()
