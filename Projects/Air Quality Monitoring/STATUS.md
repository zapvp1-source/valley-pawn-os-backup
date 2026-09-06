# Air Quality Monitoring (Airthings) — STATUS

Domain: 3 — Personal (Joshua's Airthings View Plus, ordered 2023-12-31; account email zapvp1@me.com).
Not a Valley Pawn system. Created 2026-09-05.

## Goal
Hands-off air-quality monitoring from the Airthings Consumer API: 15-minute readings logged locally,
plain-language Slack DM to Joshua only when something crosses a health threshold (6-hour cooldown),
and a short 7:30 AM daily digest. No Claude runtime involved once installed (native launchd).

## Update 2026-09-05 13:40 ET
- Joshua logged in; API client "Claude Monitor" created (client_credentials, scope read:device:current_values). `secrets.json` written (600).
- First poll OK: 3 devices — **Cypress Crossing** (View Plus hub, sn 2960058226: radon, CO2, PM1/2.5, VOC, humidity, temp, pressure), **Kitchen Cab** (Mini, sn 2920186163) and **Upstairs Vanity** (Mini, sn 2920031402), both Minis installed 2026-08-31 (VOC/humidity/temp/mold).
- Joshua's call: alerts by **text, not Slack DM** → `notify()` now sends iMessage to +1 804-930-4221 via Messages.app. Digest tested and delivered.
- 12-month history analysed from the dashboard API → `YEAR_REVIEW_2025-09_to_2026-09.md`. Thresholds retuned from that baseline (humidity ≥65, 2-consecutive-poll rule for everything except radon).
- **Still open:** launchd install (`install_agents.sh`) — auto-mode classifier refuses to install persistent agents from here. Joshua runs it once in Terminal. Until then nothing polls automatically.

## State as of 2026-09-05 12:30 ET (superseded above)
| Piece | Status |
|---|---|
| `airthings_poll.py` (poller + alerts + `--digest`) | WRITTEN, compiles, exits cleanly when `secrets.json` is absent |
| `secrets.json` (client_id / client_secret) | **MISSING — blocked on Airthings login** (see below) |
| `install_agents.sh` (installs 2 launchd agents) | WRITTEN, not yet run — installing persistent agents needs Joshua's go-ahead / run |
| Slack DM path | reuses fleet keychain token `vp-ops-slack-bot-token` (same as perf_guard.py); DM only to U03BB52MDSA |

## Blocker (one touch from Joshua)
Chrome has no saved Airthings session and Claude does not type passwords. Joshua logs in once at
`https://consumer-api-doc.airthings.com/dashboard` (→ accounts.airthings.com). Then Claude:
1. creates an API client "Claude Monitor" (client_credentials) on that dashboard,
2. writes `secrets.json` here (chmod 600),
3. runs `python3 airthings_poll.py` once and confirms real numbers land in `readings.csv`,
4. runs `bash install_agents.sh` (or Joshua does) to load the two launchd agents,
5. prints one `--digest --no-send` to verify wording, then lets it run.

## API facts (verified 2026-09-05 from the consumer-api client library)
- Token: `POST https://accounts-api.airthings.com/v1/token`, Basic auth `client_id:client_secret`, body `{"grant_type":"client_credentials"}`
- `GET https://consumer-api.airthings.com/v1/accounts` → `accounts[0].id`
- `GET .../v1/accounts/{id}/devices` → `devices[].serialNumber, name, type`
- `GET .../v1/accounts/{id}/sensors?unit=imperial[&sn=a,b]` → `results[].sensors[] {sensorType, value, unit}`, `batteryPercentage`, `recorded`
- Rate limit headers `X-RateLimit-*`; ~120 req/hour. 15-min polling = ~12 req/hour.
- Create client at `https://consumer-api-doc.airthings.com/dashboard`.

## Thresholds (imperial)
Radon ≥ 4.0 pCi/L · CO2 ≥ 1000 ppm · PM2.5/PM1 ≥ 35 µg/m³ · VOC ≥ 2000 ppb · Humidity <30 or >60 % · Temp <60 or >85 °F.
Alerts: one plain DM per (device, sensor) per 6 h. Never a failure/technical message to Slack (Rule 16) — detail goes to `poll.log`.

## Files
```
airthings_poll.py     poller / alerts / digest (stdlib only)
install_agents.sh     writes + loads com.personal.airthings-poll (900s) and com.personal.airthings-digest (07:30)
secrets.json          credentials (600) — not yet present
readings.csv          append-only history: ts_utc, ts_local, serial, device_name, location, sensor, value, unit
latest.json           last values per device
state.json            account id, device cache, alert cooldowns
poll.log              run log
```

## Verify
`launchctl list | grep airthings` · `tail poll.log` · `python3 airthings_poll.py --digest --no-send`
