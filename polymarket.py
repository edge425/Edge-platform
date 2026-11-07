
"""EDGE Polymarket trader data collector.

Collects the public sports leaderboard and each trader's
public positions and recent trades.

Python 3.10+. No third-party packages required.
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = "https://data-api.polymarket.com"
OUTPUT = "edge_polymarket_sample.json"


def fetch(path, **params):
    query = urllib.parse.urlencode(params)
    url = BASE + path + ("?" + query if query else "")

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "EDGE-Research/0.3",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def leaderboard(limit=25):
    return fetch(
        "/v2/leaderboard",
        category="SPORTS",
        timePeriod="WEEK",
        orderBy="PNL",
        limit=limit,
    )



def positions(wallet):
    response = fetch(
        "/v2/positions",
        user=wallet,
        limit=100,
        status="OPEN",
    )
        return response.get("data", [])


def trades(wallet):
    response = fetch(
        "/v2/trades",
        user=wallet,
        limit=100,
    )
        return response.get("data", [])

    


def get_wallet(trader):
    for key in ("user_id", "proxyWallet", "proxy_wallet", "wallet", "address"):
        value = trader.get(key)
        if isinstance(value, str) and value.startswith("0x"):
            return value
    return None


def main():
    result = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": "Polymarket public Data API",
        "verified_live": False,
        "leaderboard_period": "WEEK",
        "leaderboard": [],
        "leaderboard_count": 0,
        "traders": [],
        "notes": [
            "Leaderboard PNL is reported by Polymarket.",
            "Leaderboard rankings do not prove sports-only realized profit.",
            "Trader positions can include non-sports markets.",
            "Positions are snapshots, not necessarily new bets.",
            "Recent trades are not a complete betting history.",
            "Win rates require verified settled outcomes.",
        ],
    }

    try:
        leaders = leaderboard()

        if isinstance(leaders, dict):
            leaders = (
                leaders.get("data")
                or leaders.get("leaderboard")
                or leaders.get("results")
            )

        if not isinstance(leaders, list):
            raise ValueError("Invalid leaderboard response")

        result["leaderboard"] = leaders
        result["leaderboard_count"] = len(leaders)
        result["verified_live"] = True

    except Exception as exc:
        result["error"] = str(exc)

    if result["verified_live"]:
        for index, trader in enumerate(result["leaderboard"], start=1):
            if not isinstance(trader, dict):
                continue

            wallet = get_wallet(trader)

            entry = {
                "rank": index,
                "wallet": wallet,
                "name": (
                    trader.get("userName")
                    or trader.get("username")
                    or trader.get("name")
                    or (wallet[:10] if wallet else "Unknown trader")
                ),
                "leaderboard": trader,
                "positions": [],
                "trades": [],
                "errors": [],
            }

            if wallet:
                try:
                    data = positions(wallet)
                    if isinstance(data, list):
                        entry["positions"] = data
                    else:
                        entry["errors"].append(
                            "Unexpected positions response"
                        )
                except Exception as exc:
                    entry["errors"].append(
                        "Positions: " + str(exc)
                    )

                time.sleep(0.2)

                try:
                    data = trades(wallet)
                    if isinstance(data, list):
                        entry["trades"] = data
                    else:
                        entry["errors"].append(
                            "Unexpected trades response"
                        )
                except Exception as exc:
                    entry["errors"].append(
                        "Trades: " + str(exc)
                    )

                time.sleep(0.2)
            else:
                entry["errors"].append(
                    "No valid public wallet found"
                )

            result["traders"].append(entry)

            print(
                f"Trader {index}/{len(leaders)}: "
                f"{entry['name']} | "
                f"{len(entry['positions'])} positions | "
                f"{len(entry['trades'])} trades"
            )

    result["trader_count"] = len(result["traders"])
    result["position_count"] = sum(
        len(t["positions"]) for t in result["traders"]
    )
    result["trade_count"] = sum(
        len(t["trades"]) for t in result["traders"]
    )

    with open(OUTPUT, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    print("EDGE collection finished")
    print("Traders:", result["trader_count"])
    print("Positions:", result["position_count"])
    print("Trades:", result["trade_count"])

    if not result["verified_live"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
