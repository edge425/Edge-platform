# EDGE — Real-data foundation (research build)

This is a **data collector**, not a replacement website. Keep the existing EDGE Version 6 design online.

## What is included
- `polymarket.py` — read-only calls to public Polymarket leaderboard, positions, activity and trades endpoints.
- `edge-original-v6.html` — exact original uploaded Version 6 page, preserved unchanged.
- `edge-logo.png` — the last white/green sports logo image.

## Run
Requires Python 3.10+ and internet access. From the folder:

```bash
python polymarket.py
```

The program writes `edge_polymarket_sample.json` and reports an error if the API cannot be reached. No fabricated traders or results are inserted. No API keys are required for these public endpoints.

## Important next engineering work
1. Verify current API endpoint schemas and allowed commercial usage against official Polymarket documentation.
2. Add pagination, rate-limit handling, caching, sports-event filtering, and source links.
3. Reconcile trade fills, purchases, sales, redemption, fees and settlements to compute reliable **realized** P&L and win/loss records.
4. Build a server-side API for the original EDGE UI; do not treat current position value as initial stake.
5. Add Kalshi and sportsbook adapters **only with appropriate data rights and permissions**.

This collector has passed Python syntax compilation, but the API could not be reached from the current build environment, so live output is not yet validated.
