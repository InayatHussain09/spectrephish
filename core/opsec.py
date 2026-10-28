"""
SpectrePhish :: core/opsec.py
Preflight checks, header hygiene and sandbox heuristics.

Offensive logic: a campaign fails before the first click if SPF, DMARC or TLS
are wrong. Check them before sending, not after. And flag which opens are
probably mail-gateway sandboxes rather than humans.

Author : Inayat Hussain
"""

from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone

from config import SANDBOX_UA_HINTS

try:
    import dns.resolver
    DNS_OK = True
except Exception:
    DNS_OK = False


def _txt(name: str) -> list:
    if not DNS_OK:
        return []
    try:
        return [b"".join(r.strings).decode(errors="ignore")
                for r in dns.resolver.resolve(name, "TXT")]
    except Exception:
        return []


def check_dns(domain: str) -> list:
    findings = []
    spf = [r for r in _txt(domain) if r.lower().startswith("v=spf1")]
    dmarc = [r for r in _txt("_dmarc." + domain) if r.lower().startswith("v=dmarc1")]
    if not spf:
        findings.append(("warn", f"no SPF record on {domain}"))
    else:
        policy = spf[0].lower()
        findings.append(("ok", f"SPF present: {policy[:60]}"))
        if policy.strip().endswith("~all"):
            findings.append(("warn", "SPF softfail (~all) -- spoofed mail may be quarantined"))
        elif not policy.strip().endswith("-all"):
            findings.append(("warn", "SPF has no strict -all"))
    if not dmarc:
        findings.append(("warn", f"no DMARC record on {domain}"))
    else:
        findings.append(("ok", f"DMARC present: {dmarc[0][:60]}"))
    return findings


def check_tls(host: str, port: int = 443) -> list:
    findings = []
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as tls:
                cert = tls.getpeercert()
        issuer = dict(x[0] for x in cert.get("issuer", []))
        not_after = cert.get("notAfter", "")
        findings.append(("ok", f"TLS valid on {host}:{port} "
                               f"(issuer {issuer.get('organizationName', 'unknown')})"))
        try:
            expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(
                tzinfo=timezone.utc)
            days = (expiry - datetime.now(timezone.utc)).days
            if days < 14:
                findings.append(("warn", f"certificate expires in {days} days"))
        except Exception:
            pass
    except Exception as exc:
        findings.append(("warn", f"TLS check failed on {host}:{port} -- {exc}"))
    return findings


def check_port(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=5):
            return True
    except OSError:
        return False


def header_hygiene(profile: dict) -> list:
    findings = []
    from_addr = (profile.get("from_addr") or "")
    reply_to = (profile.get("reply_to") or "")
    xmailer = (profile.get("xmailer") or "")

    if not from_addr or "@" not in from_addr:
        findings.append(("warn", "no From address -- defaults to the SMTP username"))
    if reply_to and "@" in from_addr and reply_to.split("@")[-1] != from_addr.split("@")[-1]:
        findings.append(("warn", "Reply-To domain differs from From domain -- visible mismatch"))
    if not xmailer:
        findings.append(("warn", "no X-Mailer -- a bare relay header stands out"))
    else:
        findings.append(("ok", f"X-Mailer set to '{xmailer}'"))
    if (profile.get("tls") or "").lower() == "none":
        findings.append(("warn", "plaintext SMTP -- some gateways score this down"))
    else:
        findings.append(("ok", f"transport TLS mode: {profile.get('tls')}"))
    return findings


def sandbox_hint(user_agent: str, ip: str) -> bool:
    ua = (user_agent or "").lower()
    if any(h in ua for h in SANDBOX_UA_HINTS):
        return True
    if not ua:
        return True
    if "windows nt" in ua and "trident" not in ua and "edge" not in ua:
        return False
    if "iphone" in ua or "android" in ua or "macintosh" in ua:
        return False
    return True


def preflight(profile: dict, base_url: str) -> list:
    findings = []
    domain = (profile.get("from_addr") or "").split("@")[-1]
    if domain:
        findings += check_dns(domain)

    host = (profile.get("host") or "").split(":")[0]
    if host:
        port = int(profile.get("port") or 587)
        findings.append(("ok", f"SMTP reachable: {host}:{port}")
                        if check_port(host, port)
                        else ("warn", f"SMTP {host}:{port} not reachable from here"))

    if base_url:
        host = base_url.split("//")[-1].split("/")[0].split(":")[0]
        findings += check_tls(host, 443)

    findings += header_hygiene(profile)
    return findings


def checklist_landing(base_url: str) -> list:
    findings = []
    host = base_url.split("//")[-1].split("/")[0].split(":")[0]
    if host in ("127.0.0.1", "localhost"):
        findings.append(("warn", "tracking URL is localhost -- the target cannot reach it"))
    if base_url.startswith("http://"):
        findings.append(("warn", "tracking over plain HTTP -- HTTPS looks more legitimate"))
    return findings
