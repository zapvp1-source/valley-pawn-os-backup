#!/bin/bash
# com.valleypawn.ebay-customer-campaign — "Shop Us Online" monthly eBay customer campaign (2026-09-29).
# 24th of each month 09:15: builds NEXT month's pack, creates the Brevo email, runs the house
# preflight, SCHEDULES it for the 1st Tuesday 10:00 ET (Joshua: "automate this"), sends Bravo's
# marketing team the push + text request (if enabled in config.json), then one plain FYI DM.
# Failure: logged only, no Slack (Rule 16); the next run retries (build is idempotent).
#   ebay_customer_campaign.sh                  next month
#   ebay_customer_campaign.sh --month 2026-10  specific month (catch-up)
AGENT="ebay-customer-campaign"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
C="$HOME/Documents/Claude/Projects/eBay Customer Campaign"
vp_lock "$AGENT" 30
MONTH=""; [ "$1" = "--month" ] && MONTH="$2"
[ -z "$MONTH" ] && MONTH=$(date -v+1m +%Y-%m)
L="$VLOG/$AGENT.log"; echo "=== $(date '+%F %T') run for $MONTH" >>"$L"
cd "$C" || exit 1
"$PY" build_month.py --month "$MONTH" --schedule >>"$L" 2>&1 || { echo "build/schedule FAILED for $MONTH" >>"$L"; exit 1; }
"$PY" bravo_request.py "$MONTH" >>"$L" 2>&1
"$PY" build_text_lists.py "$MONTH" >>"$L" 2>&1 || echo "text lists FAILED for $MONTH (held, not partial)" >>"$L"
TL=$("$PY" -c "import json;s=json.load(open('packs/$MONTH/text_lists.json'))['stores'];print(sum(s.values()))" 2>/dev/null)
BR=$([ -f "packs/$MONTH/bravo_request_sent.json" ] && echo yes || echo no)
P="packs/$MONTH"
SUBJ=$(grep -m1 '^Email subject:' "$P/PACK.md" | sed 's/Email subject: \*\*//; s/\*\*$//')
WHEN=$("$PY" -c "import json,datetime as d;s=json.load(open('$P/brevo_state.json'));t=s.get('scheduledAt') or s.get('intended') or '';print(d.datetime.fromisoformat(t.replace('Z','+00:00')).astimezone().strftime('%a %b %-d at %-I:%M %p') if t else s.get('status',''))" 2>/dev/null)
PUSHD=$(grep -m1 '| 2 | Push' "$P/PACK.md" | cut -d'|' -f4 | xargs)
SMSD=$(grep -m1 '| 3 | Text' "$P/PACK.md" | cut -d'|' -f4 | xargs)
if [ "$BR" = yes ]; then
  MSG="Shop Us Online for $MONTH is set. Email \"$SUBJ\" goes out $WHEN. Bravo has the push request for $PUSHD. Texts go out through Chekkit on $SMSD ($TL customers)."
else
  PT=$(grep -m1 '^TITLE' "$P/push.txt" | sed 's/^TITLE ([0-9]*\/40): //'); PB=$(grep -m1 '^BODY' "$P/push.txt" | sed 's/^BODY ([0-9]*\/120): //'); PL=$(grep -m1 '^LINK' "$P/push.txt" | sed 's/^LINK: //'); TX=$(tail -1 "$P/sms.txt")
  MSG="Shop Us Online for $MONTH is set. Email \"$SUBJ\" goes out $WHEN.

Push for $PUSHD: $PT — $PB
$PL

Text for $SMSD ($TL numbers across the 5 stores, Chekkit lists ready):
$TX"
fi
if [ -f "$P/dm_sent" ]; then echo "DM already sent for $MONTH" >>"$L"; else
  "$PY" "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_slack.py" dm "$MSG" >>"$L" 2>&1 && date '+%F %T' > "$P/dm_sent"
fi
echo "$(date '+%F %T') $MONTH done (bravo request: $BR)" >>"$L"
