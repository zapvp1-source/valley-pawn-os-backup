# Connect GunBroker sold prices (one-time, about 5 minutes)

Why: GunBroker completed-auction prices are the most accurate used-gun market data (the data True Gun Value
republishes). GunBroker's API is the licensed way to use it in our reports.

1. Sign in to GunBroker with the company account and open https://api.gunbroker.com/User/DevKey/Create
   to get a free developer key.
2. Create the file `Valuation Core/.gunbroker_credentials.json` with:

```json
{"dev_key": "PASTE-KEY", "username": "COMPANY-GUNBROKER-USERNAME", "password": "COMPANY-GUNBROKER-PASSWORD"}
```

3. Test: `python3 gun_value.py "GLOCK 19 GEN 5" Pistol` → the basis line should say "GunBroker".

What it does: at most 150 look-ups a day, each cached 14 days; only listings that actually sold, used
condition, last 30 days, parts/magazines/holsters filtered out. Nothing is ever listed, bought or bid.
If the key or login stops working, the reports quietly fall back to our own gun sales.
