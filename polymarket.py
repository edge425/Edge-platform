"""EDGE public Polymarket sports leaderboard collector (Python 3.10+).

Writes edge_polymarket_sample.json. No third-party dependencies.
A successful workflow requires a successful API response; errors exit nonzero.
Leaderboard PNL is not proof of sports-only settled-bet profitability.
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = "https://data-api.polymarket.com"
OUTPUT = "edge_polymarket_sample.json"


def fetch(path, **params):
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "EDGE-Research/0.2", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)




def leaderboard(limit=25, period="WEEK"):
    """Fetch the public Polymarket sports leaderboard."""
    return fetch(
        "/v2/leaderboard",
        category="SPORTS",
        timePeriod=period,
        orderBy="PNL",
        limit=min(max(int(limit), 1), 50),
        
    )





def positions(wallet, limit=100):
    return fetch("/positions", user=wallet, limit=min(int(limit), 500), offset=0)


def activity(wallet, limit=100):
    return fetch("/activity", user=wallet, limit=min(int(limit), 500), offset=0)


def trades(wallet, limit=100):
    return fetch("/trades", user=wallet, limit=min(int(limit), 500), offset=0)


def main():
    result = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": "Polymarket public Data API",
        "verified_live": False,
        "notes": [
            "Leaderboard PNL may not equal independently verified sports-only realized profit.",
            "Transactions do not equal settled bets; do not infer win rates from trade counts.",
            "Historical activity and positions may require pagination and market matching.",
        ],
    }
    try:
        leaders = leaderboard()
        if isinstance(leaders, dict):
    print("API response keys:", list(leaders.keys()))
    leaders = leaders.get("data", leaders.get("leaderboard", leaders.get("results")))
if not isinstance(leaders, list):
    raise ValueError("Leaderboard response does not contain a recognized trader list")
        result["leaderboard"] = leaders
        result["leaderboard_count"] = len(leaders)
        result["verified_live"] = True
    except (urllib.error.URLError, ValueError, TypeError) as exc:
        result["error"] = str(exc)
    with open(OUTPUT, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in result.items() if k != "leaderboard"}, indent=2))
    if not result["verified_live"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
