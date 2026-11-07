"""EDGE Polymarket public-data collector. Python 3.10+, no dependencies.
Data is not guaranteed complete; do not infer bet-level wins from trades.
"""
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = 'https://data-api.polymarket.com'

def fetch(path, **params):
    url = BASE + path + '?' + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={'User-Agent': 'EDGE-Research/0.1', 'Accept': 'application/json'})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)

def leaderboard(limit=25, period='WEEK'):
    """Public leaderboard. SPORTS filter may not cover all sports-only performance."""
    /v2/leaderboard, category='SPORTS', timePeriod=period,
                 orderBy='PNL', limit=min(int(limit), 50), offset=0)

def positions(wallet, limit=100):
    """Current wallet positions, not necessarily original money wagered."""
    return fetch('/positions', user=wallet, limit=min(int(limit), 500), offset=0)

def activity(wallet, limit=100):
    """Wallet transaction activity; trade rows are NOT individual settled bets."""
    return fetch('/activity', user=wallet, limit=min(int(limit), 500), offset=0)

def trades(wallet, limit=100):
    """Trades for a wallet. Returns partial history when pagination is required."""
    return fetch('/trades', user=wallet, limit=min(int(limit), 500), offset=0)

def main():
    result = {'retrieved_at': datetime.now(timezone.utc).isoformat(),
              'source': 'Polymarket public Data API', 'verified_live': False,
              'notes': ['Leaderboard ranking may not represent sports-only realized net profit.',
                        'Transactions are not equivalent to settled bets.',
                        'Historical data may require pagination and market resolution matching.']}
    try:
        leaders = leaderboard()
        result['leaderboard'] = leaders
        result['verified_live'] = True
        result['leaderboard_count'] = len(leaders) if isinstance(leaders, list) else None
    except Exception as exc:
        result['error'] = str(exc)
    with open('edge_polymarket_sample.json', 'w') as file:
        json.dump(result, file, indent=2)
    print(json.dumps({k:v for k,v in result.items() if k != 'leaderboard'}, indent=2))

if __name__ == '__main__':
    main()
