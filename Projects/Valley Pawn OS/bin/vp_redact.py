#!/usr/bin/env python3
"""vp_redact.py — strip session tokens / secrets / card numbers from saved browser pages (2026-10-22).

WHY: purchasing/runs/<stamp>/*.html were raw Amazon checkout DOM dumps (page.content()). Every page carried
inline <script> blobs, anti-CSRF tokens, session ids and hidden-input tokens, and two random Amazon element
ids happened to match the backup's secret scanner (a data-csa-c-id containing "xoxp-", a cel_widget_id=uuid),
which stopped the 10/22 00:15 nightly backup. Debug HTML never needs any of that: keep the visible markup,
drop the credentials.

    redact_html(text) -> text           (used by supply_order.shot() before anything touches disk)
    vp_redact.py <file.html> [...]       redact files IN PLACE (caller backs them up first)

Idempotent. Never raises on odd markup (falls back to the pattern pass only).
"""
import re
import sys

R = "[REDACTED]"

# same families as bin/secret_scan.py (kept in sync by hand; a scan hit on a redacted page is a bug here)
SECRET_PATTERNS = [
    r'AKIA[0-9A-Z]{16}',
    r'xox[baprs]-[A-Za-z0-9-]{10,}',
    r'hooks\.slack\.com/services/[A-Za-z0-9/]+',
    r'(discord(app)?\.com/api/webhooks/|hooks\.zapier\.com)[A-Za-z0-9/]+',
    r'gh[pousr]_[A-Za-z0-9]{20,}',
    r'SG\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}',
    r'[sp]k_live_[A-Za-z0-9]{10,}',
    r'PRD-[A-Za-z0-9]{6,}',
    r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
]
SECRET_RE = re.compile("|".join("(?:%s)" % p for p in SECRET_PATTERNS))
# KEY = "uuid" / key: 'value' shapes the scanner treats as credentials
KV_RE = re.compile(r'(?i)\b((?:[A-Z_]*_ID|api[_-]?key|secret[_-]?key|client[_-]?secret|password|token|bearer|authorization)'
                   r'\s*[:=]\s*)([\'"])[^\'"\n]{4,}?\2')
SCRIPT_RE = re.compile(r'(?is)<script\b[^>]*>.*?</script\s*>')
NOSCRIPT_RE = re.compile(r'(?is)<noscript\b[^>]*>.*?</noscript\s*>')
# any tag whose attributes mention csrf/token/session/auth: blank every value/content attribute in it
SENSITIVE_TAG_RE = re.compile(r'(?is)<(?:input|meta)\b[^>]*>')
SENSITIVE_WORD_RE = re.compile(r'(?i)csrf|token|session|auth|nonce|signature|secret|password|ubid|customer[-_]?id')
VALUE_ATTR_RE = re.compile(r'(?is)\b(value|content)\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)')
HIDDEN_RE = re.compile(r'(?i)type\s*=\s*["\']?hidden')
# data-*/id attributes that carry tokens (e.g. data-csrf-token, data-encrypted-token)
DATA_TOKEN_ATTR_RE = re.compile(r'(?is)\b(data-[\w-]*(?:csrf|token|session|nonce|signature)[\w-]*)\s*=\s*("[^"]*"|\'[^\']*\')')
PAN_RE = re.compile(r'(?<![\d-])([3456]\d{12,18})(?![\d-])')


def _luhn(n):
    s, alt = 0, False
    for ch in reversed(n):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        s += d
        alt = not alt
    return s % 10 == 0


def _tag(m):
    t = m.group(0)
    if HIDDEN_RE.search(t) or SENSITIVE_WORD_RE.search(t) or re.search(r'(?i)type\s*=\s*["\']?password', t):
        t = VALUE_ATTR_RE.sub(lambda v: '%s="%s"' % (v.group(1), R), t)
    return t


def redact_html(text):
    if not isinstance(text, str):
        return text
    try:
        text = SCRIPT_RE.sub("<script>/* removed by vp_redact */</script>", text)
        text = NOSCRIPT_RE.sub("", text)
        text = SENSITIVE_TAG_RE.sub(_tag, text)
        text = DATA_TOKEN_ATTR_RE.sub(lambda m: '%s="%s"' % (m.group(1), R), text)
    except Exception:
        pass
    text = SECRET_RE.sub(R, text)
    text = KV_RE.sub(lambda m: m.group(1) + m.group(2) + R + m.group(2), text)
    text = PAN_RE.sub(lambda m: R if _luhn(m.group(1)) and 13 <= len(m.group(1)) <= 19 else m.group(1), text)
    return text


def redact_file(path):
    with open(path, errors="replace") as fh:
        s = fh.read()
    out = redact_html(s)
    if out != s:
        tmp = path + ".redact.tmp"
        with open(tmp, "w") as fh:
            fh.write(out)
        import os
        os.replace(tmp, path)
        return True
    return False


if __name__ == "__main__":
    n = 0
    for p in sys.argv[1:]:
        if redact_file(p):
            n += 1
    print("redacted %d of %d file(s)" % (n, len(sys.argv) - 1))
