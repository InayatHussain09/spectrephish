#!/usr/bin/env python3
"""
SpectrePhish :: main.py
Phishing Operator Framework -- CLI entry point.

Author : Inayat Hussain  (Red Team Operator & Offensive Security Engineer)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import signal
import sys
import time

from config import (
    DEFAULT_BATCH, DEFAULT_DELAY, DEFAULT_LANDING_HTML, DEFAULT_LISTEN,
    DEFAULT_PORT, DEFAULT_TEMPLATE_HTML, DEFAULT_TEMPLATE_SUBJECT,
    DEFAULT_TEMPLATE_TEXT, DEFAULT_TIMEOUT, EXPORT_DIR, LANDING_DIR, PAYLOAD_DIR,
    TEMPLATE_DIR, C,
)
from core import payloads, ui
from core.landing import detect_fields, mirror, save_landing
from core.mailer import Mailer
from core.opsec import preflight
from core.render import prepare_email, render, strip_tags, target_context
from core.server import CampaignServer
from core.store import Store
from core.targets import export_csv, import_csv

store = Store()


# ==========================================================================
def cmd_init(args) -> int:
    ui.banner()
    ui.phase(1, 1, "initialise")
    for path in (TEMPLATE_DIR, LANDING_DIR, PAYLOAD_DIR, EXPORT_DIR):
        os.makedirs(path, exist_ok=True)

    store.upsert_template("notification", DEFAULT_TEMPLATE_SUBJECT,
                          DEFAULT_TEMPLATE_HTML, DEFAULT_TEMPLATE_TEXT)
    store.upsert_landing("login", DEFAULT_LANDING_HTML,
                         capture=detect_fields(DEFAULT_LANDING_HTML), redirect_url="")
    ui.ok("data directories created")
    ui.ok("default template 'notification' installed")
    ui.ok("default landing 'login' installed")
    ui.line(f"store: {store.path}", (C.DIMC,))
    ui.line("next: spectrephish seed --all   (installs the 80-asset catalog)", (C.GREY,))
    return 0


def cmd_seed(args) -> int:
    """init + the entire catalog, in one command."""
    ui.banner()
    ui.phase(1, 3, "initialise")
    for path in (TEMPLATE_DIR, LANDING_DIR, PAYLOAD_DIR, EXPORT_DIR):
        os.makedirs(path, exist_ok=True)
    store.upsert_template("notification", DEFAULT_TEMPLATE_SUBJECT,
                          DEFAULT_TEMPLATE_HTML, DEFAULT_TEMPLATE_TEXT)
    store.upsert_landing("login", DEFAULT_LANDING_HTML,
                         capture=detect_fields(DEFAULT_LANDING_HTML), redirect_url="")
    ui.ok("data directories + core template/landing")

    ui.phase(2, 3, "email templates")
    from core.generate import generate_templates
    tnames = generate_templates(store)
    ui.ok(f"{len(tnames)} built-in templates installed")

    ui.phase(3, 3, "landing variants")
    from core.generate import generate_landings
    lnames = generate_landings(store)
    ui.ok(f"{len(lnames)} landing variants installed")

    ui.line("next: spectrephish template list | landing list", (C.GREY,))
    ui.line("then: profile add / targets import / campaign create", (C.GREY,))
    return 0


# ==========================================================================
def cmd_targets(args) -> int:
    ui.banner()
    if args.action == "import":
        target = args.file or args.file_opt
        added, skipped = import_csv(store, target)
        ui.ok(f"imported {added} new target(s), skipped {skipped}")
    elif args.action == "list":
        rows = [(t["id"], t["email"], t["first_name"], t["last_name"], t["position"])
                for t in store.targets()]
        ui.section("targets")
        ui.end_section()
        ui.table(("id", "email", "first", "last", "position"), rows)
        ui.line(f"{len(rows)} target(s)", (C.DIMC,))
    elif args.action == "export":
        path = export_csv(store, args.file or args.file_opt)
        ui.ok(f"exported to {path}")
    elif args.action == "clear":
        for t in store.targets():
            store.delete_target(t["id"])
        ui.ok("all targets removed")
    return 0


# ==========================================================================
def cmd_profile(args) -> int:
    ui.banner()
    if args.action == "list":
        rows = [(p["id"], p["name"], p["host"], p["port"], p["tls"],
                 p["from_addr"] or p["username"] or "") for p in store.profiles()]
        ui.table(("id", "name", "host", "port", "tls", "from"), rows)
        return 0

    if args.action == "show":
        p = store.profile_by_name(args.name)
        if not p:
            ui.err(f"no profile '{args.name}'")
            return 1
        ui.card(p["name"], [(k, p[k]) for k in
                            ("host", "port", "username", "tls", "from_name",
                             "from_addr", "reply_to", "delay", "xmailer")])
        return 0

    if args.action == "delete":
        store._exec("DELETE FROM profiles WHERE name=?", (args.name,))
        ui.ok(f"deleted profile '{args.name}'")
        return 0

    if args.action == "add":
        store.upsert_profile(
            args.name, host=args.host, port=args.port, username=args.username,
            password=args.password or "", tls=args.tls,
            from_name=args.from_name or "", from_addr=args.from_addr or "",
            reply_to=args.reply_to or "", delay=args.delay, batch=args.batch,
            xmailer=args.xmailer)
        ui.ok(f"profile '{args.name}' saved")

    if args.action == "check":
        p = store.profile_by_name(args.name)
        if not p:
            ui.err(f"no profile '{args.name}'")
            return 1
        ui.section(f"opsec preflight · {p['name']}")
        ui.end_section()
        for level, message in preflight(p, args.url or ""):
            (ui.ok if level == "ok" else ui.warn)(message)
    return 0


# ==========================================================================
def cmd_template(args) -> int:
    ui.banner()

    if args.action == "categories":
        from core.defaults import EMAIL_TEMPLATES, categories
        for cat in categories():
            count = sum(1 for t in EMAIL_TEMPLATES if t["category"] == cat)
            ui.bullet(f"{cat}  ({count})", (C.GREY,))
        ui.line(f"{len(EMAIL_TEMPLATES)} templates in the catalog", (C.DIMC,))
        return 0

    if args.action == "generate":
        from core.defaults import email_names
        from core.generate import generate_templates
        overrides = {}
        if args.from_name:
            overrides["from_name"] = args.from_name
        if args.subject:
            overrides["subject"] = args.subject
        if args.cta:
            overrides["cta"] = args.cta
        if args.url:
            overrides["url"] = args.url
        names = [args.name] if args.name else None
        written = generate_templates(store, names=names, category=args.category,
                                     overrides=overrides)
        if not written:
            ui.warn("nothing matched -- check --name / --category")
            return 1
        for name in written:
            ui.ok(name)
        ui.line(f"{len(written)} of {len(email_names())} catalog templates installed",
                (C.DIMC,))
        return 0

    if args.action == "list":
        rows = [(t["id"], t["name"], t["subject"][:52]) for t in store.templates()]
        ui.table(("id", "name", "subject"), rows)
        ui.line(f"{len(rows)} installed", (C.DIMC,))
        return 0

    if args.action == "show":
        t = store.template_by_name(args.name)
        if not t:
            ui.err(f"no template '{args.name}'")
            return 1
        ui.card(t["name"], [("subject", t["subject"]), ("html bytes", len(t["html"]))])
        ui.line(strip_tags(t["html"])[:600], (C.GREY,))
        return 0

    if args.action == "delete":
        store._exec("DELETE FROM templates WHERE name=?", (args.name,))
        ui.ok(f"deleted template '{args.name}'")
        return 0

    if args.action in ("import", "add"):
        html, text = "", ""
        if args.file:
            with open(args.file, encoding="utf-8", errors="ignore") as handle:
                html = handle.read()
        elif args.html:
            html = args.html
        if args.text_file:
            with open(args.text_file, encoding="utf-8", errors="ignore") as handle:
                text = handle.read()
        subject = args.subject or DEFAULT_TEMPLATE_SUBJECT
        store.upsert_template(args.name, subject, html, text or strip_tags(html),
                              attachments=args.attach or [])
        ui.ok(f"template '{args.name}' saved")
        if not text:
            ui.bullet("plaintext part auto-derived from the HTML", (C.DIMC,))
    return 0


# ==========================================================================
def cmd_landing(args) -> int:
    ui.banner()

    if args.action == "generate":
        from core.generate import generate_landings
        overrides = {}
        if args.brand:
            overrides["brand"] = args.brand
        if args.title:
            overrides["title"] = args.title
        names = [args.name] if args.name else None
        written = generate_landings(store, names=names, overrides=overrides,
                                    redirect=args.redirect or "")
        if not written:
            ui.warn("nothing matched")
            return 1
        for name in written:
            ui.ok(name)
        ui.line(f"{len(written)} landing variant(s) installed", (C.DIMC,))
        return 0

    if args.action == "list":
        rows = [(l["id"], l["name"], l["redirect_url"] or "-") for l in store.landings()]
        ui.table(("id", "name", "redirect"), rows)
        ui.line(f"{len(rows)} installed", (C.DIMC,))
        return 0

    if args.action == "show":
        l = store.landing_by_name(args.name)
        if not l:
            ui.err(f"no landing '{args.name}'")
            return 1
        ui.card(l["name"], [("redirect", l["redirect_url"] or "-"),
                            ("fields", ", ".join(detect_fields(l["html"])) or "-")])
        return 0

    if args.action == "delete":
        store._exec("DELETE FROM landings WHERE name=?", (args.name,))
        ui.ok(f"deleted landing '{args.name}'")
        return 0

    if args.action == "mirror":
        ui.line(f"mirroring {args.url} ...", (C.GREY,))
        html = mirror(args.url, inline_assets=not args.no_assets)
        save_landing(args.name, html)
        fields = detect_fields(html)
        store.upsert_landing(args.name, html, capture=fields,
                             redirect_url=args.redirect or "",
                             redirect_on_submit=bool(args.redirect))
        ui.ok(f"landing '{args.name}' mirrored ({len(html)} bytes)")
        ui.bullet(f"captured fields: {', '.join(fields) or 'none detected'}", (C.GREY,))
        if args.redirect:
            ui.bullet(f"will redirect to {args.redirect}", (C.GREY,))
        return 0

    if args.action == "add":
        html = ""
        if args.file:
            with open(args.file, encoding="utf-8", errors="ignore") as handle:
                html = handle.read()
        save_landing(args.name, html)
        store.upsert_landing(args.name, html, capture=detect_fields(html),
                             redirect_url=args.redirect or "",
                             redirect_on_submit=bool(args.redirect))
        ui.ok(f"landing '{args.name}' saved")
    return 0


# ==========================================================================
def cmd_campaign(args) -> int:
    ui.banner()
    if args.action == "list":
        rows = []
        for c in store.campaigns():
            s = store.stats(c["id"])
            rows.append((c["id"], c["name"], c["status"],
                         f"{s['sent']}/{s['total']}", s["opened"], s["clicked"],
                         s["submitted"]))
        ui.table(("id", "name", "status", "sent", "open", "click", "submit"), rows)
        return 0

    if args.action == "create":
        profile = store.profile_by_name(args.profile)
        template = store.template_by_name(args.template)
        landing = store.landing_by_name(args.landing)
        missing = [n for n, o in (("profile", profile), ("template", template),
                                  ("landing", landing)) if not o]
        if missing:
            ui.err("missing: " + ", ".join(missing))
            return 1
        cid = store.create_campaign(args.name, profile["id"], template["id"],
                                    landing["id"], args.url)
        ui.ok(f"campaign '{args.name}' created (id {cid})")
        return 0

    campaign = store.campaign_by_name(args.name)
    if not campaign:
        ui.err(f"no campaign '{args.name}'")
        return 1
    cid = campaign["id"]

    if args.action == "status":
        s = store.stats(cid)
        ui.card(campaign["name"], [
            ("status", campaign["status"]), ("url", campaign["url_base"]),
            ("sent", s["sent"]), ("opened", s["opened"]), ("clicked", s["clicked"]),
            ("submitted", s["submitted"]), ("reported", s["reported"])])
        ui.section("recent events")
        ui.end_section()
        for e in store.events(cid, 25):
            stamp = time.strftime("%H:%M:%S", time.localtime(e["ts"]))
            meta = (e["meta"] or "")[:70]
            ui.bullet(f"{stamp}  {e['kind']:<8} {e['token'][:8]}  {meta}", (C.GREY,))
        return 0

    if args.action == "add-targets":
        if args.all:
            ids = [t["id"] for t in store.targets()]
        else:
            ids = []
            for email in (args.email or []):
                t = store._row("SELECT id FROM targets WHERE email=?", (email.lower(),))
                if t:
                    ids.append(t["id"])
        added = store.add_campaign_targets(cid, ids)
        ui.ok(f"added {added} target(s) to '{campaign['name']}'")
        return 0

    if args.action == "send":
        return campaign_send(campaign, args)

    if args.action == "serve":
        return campaign_serve(campaign, args)
    return 0


def campaign_send(campaign: dict, args) -> int:
    cid = campaign["id"]
    profile = store.profile(campaign["profile_id"])
    template = store.template(campaign["template_id"])
    targets = store.campaign_targets(cid)
    if not targets:
        ui.err("no targets in this campaign -- run: campaign add-targets")
        return 1

    base = campaign["url_base"]
    if "127.0.0.1" in base or "localhost" in base:
        ui.warn("url_base is localhost -- set --url to your LAN IP for real targets")

    ui.phase(1, 3, "opsec preflight")
    for level, message in preflight(profile, base):
        (ui.ok if level == "ok" else ui.warn)(message)

    ui.phase(2, 3, "sending")
    mailer = Mailer(profile, timeout=args.timeout)
    try:
        mailer.connect()
    except Exception as exc:
        ui.err(f"SMTP connect failed: {exc}")
        return 1

    attachments = json.loads(template["attachments"] or "[]")
    sent = 0
    started = time.time()
    links = 0
    for row in targets:
        target = store._row("SELECT * FROM targets WHERE id=?", (row["target_id"],))
        if not target:
            continue
        ctx = target_context(target, base, row["token"])
        html, links = prepare_email(render(template["html"], ctx), base, row["token"])
        text = render(template["text"] or strip_tags(template["html"]), ctx)
        try:
            mailer.send(target["email"], render(template["subject"], ctx),
                        html, text, attachments)
            store.mark(cid, row["token"], "sent")
            sent += 1
        except Exception as exc:
            ui.warn(f"{target['email']}: {exc}")
        ui.progress(sent + 1, len(targets), "sent", target["email"][:28])
    mailer.close()

    store.set_status(cid, "running")
    ui.phase(3, 3, "summary")
    ui.card("send complete", [("delivered", sent), ("total", len(targets)),
                              ("elapsed", f"{time.time() - started:.1f}s"),
                              ("links per email", links)])
    ui.line(f"now run: spectrephish campaign serve {campaign['name']}", (C.GREY,))
    return 0


def campaign_serve(campaign: dict, args) -> int:
    cid = campaign["id"]
    landing_id = campaign["landing_id"]

    def on_event(kind: str, token: str, meta: dict) -> None:
        target = store.target_by_token(token)
        who = target["email"] if target else token[:8]
        flag = " [SANDBOX?]" if meta.get("sandbox") else ""
        colors = {"open": C.CYAN, "click": C.GREEN, "submit": C.MAGENTA,
                  "report": C.YELLOW}.get(kind, C.WHITE)
        print(f"   {ui.paint('▸', colors) if hasattr(ui, 'paint') else '▸'} "
              f"{kind.upper().ljust(7)} {who}{flag}  {meta.get('ip', '')}", flush=True)

    server = CampaignServer(store, cid, landing_id, listen=args.listen,
                            port=args.port, on_event=on_event)
    ui.banner()
    ui.phase(1, 1, "campaign server")
    ui.kv([("campaign", campaign["name"]),
           ("listen", f"{args.listen}:{args.port}"),
           ("landing", f"http://{args.host or args.listen}:{args.port}/s/<token>")])
    ui.end_section()
    ui.line("waiting for events -- Ctrl-C to stop", (C.DIMC,))

    def shutdown(*_):
        print()
        ui.line("stopping", (C.YELLOW,))
        server.stop()
        s = store.stats(cid)
        ui.card("final", [(k, s[k]) for k in
                          ("sent", "opened", "clicked", "submitted", "reported")])
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    server.serve_forever()
    return 0


# ==========================================================================
def cmd_payload(args) -> int:
    ui.banner()
    ui.phase(1, 1, "payload build")
    written = payloads.build_all(args.url, title=args.title)
    for path in written:
        ui.ok(os.path.basename(path))
    if args.iso:
        iso = payloads.build_iso(args.title)
        ui.ok(os.path.basename(iso)) if iso else ui.warn("genisoimage not found")
    ui.line(f"payloads served at {args.url.rstrip('/')}/payload/<file>", (C.GREY,))
    return 0


# ==========================================================================
def cmd_report(args) -> int:
    ui.banner()
    campaign = store.campaign_by_name(args.name)
    if not campaign:
        ui.err(f"no campaign '{args.name}'")
        return 1
    cid = campaign["id"]
    s = store.stats(cid)

    ui.card(campaign["name"], [
        ("status", campaign["status"]),
        ("sent", s["sent"]), ("opened", s["opened"]), ("clicked", s["clicked"]),
        ("submitted", s["submitted"]), ("reported", s["reported"])])

    def pct(n):
        return f"{(n / s['total'] * 100):.1f}%" if s["total"] else "0%"

    ui.section("funnel")
    ui.end_section()
    ui.bullet(f"delivery                {pct(s['sent'])}", (C.GREY,))
    ui.bullet(f"open rate               {pct(s['opened'])}  (includes sandbox opens)", (C.GREY,))
    ui.bullet(f"click rate              {pct(s['clicked'])}", (C.GREEN,))
    ui.bullet(f"credential capture rate {pct(s['submitted'])}", (C.MAGENTA,))

    rows = []
    for row in store.campaign_targets(cid):
        if row["opened"] or row["clicked"] or row["submitted"]:
            rows.append((row["email"], "Y" if row["opened"] else "-",
                         "Y" if row["clicked"] else "-",
                         "Y" if row["submitted"] else "-",
                         (row["captured"] or "")[:40]))
    ui.section("engaged targets")
    ui.end_section()
    ui.table(("email", "open", "click", "submit", "captured"), rows)

    if args.export:
        os.makedirs(EXPORT_DIR, exist_ok=True)
        path = (args.export if os.path.isabs(args.export)
                else os.path.join(EXPORT_DIR, args.export))
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["email", "sent", "opened", "clicked", "submitted",
                             "reported", "captured", "ip", "ua"])
            for row in store.campaign_targets(cid):
                writer.writerow([row["email"], row["sent"], row["opened"],
                                 row["clicked"], row["submitted"], row["reported"],
                                 row["captured"] or "", row["ip"] or "", row["ua"] or ""])
        ui.ok(f"exported to {path}")
    return 0


# ==========================================================================
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="spectrephish",
        description="SpectrePhish -- Phishing Operator Framework by Inayat Hussain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "quick start:\n"
            "  spectrephish seed --all\n"
            "  spectrephish profile add corp --host smtp.corp.com --username it@corp.com \\\n"
            "      --password 'x' --from-addr it@corp.com --from-name 'IT Service Desk'\n"
            "  spectrephish targets import staff.csv\n"
            "  spectrephish landing mirror o365 --url https://login.microsoftonline.com \\\n"
            "      --redirect https://login.microsoftonline.com\n"
            "  spectrephish campaign create q1 --profile corp \\\n"
            "      --template m365-password-expiry --landing o365 --url http://10.0.0.5:8080\n"
            "  spectrephish campaign add-targets q1 --all\n"
            "  spectrephish campaign send q1\n"
            "  spectrephish campaign serve q1 --host 10.0.0.5\n"
            "\n"
            "catalog:\n"
            "  spectrephish template categories\n"
            "  spectrephish template generate --all\n"
            "  spectrephish template generate --category Finance\n"
            "  spectrephish landing generate --all\n"
        ),
    )
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="create data dirs and the core template/landing")

    sd = sub.add_parser("seed", help="init + install the full 80-asset catalog")
    sd.add_argument("--all", action="store_true", help="(default) install everything")

    t = sub.add_parser("targets", help="manage targets")
    t.add_argument("action", choices=["import", "list", "export", "clear"])
    t.add_argument("file", nargs="?")
    t.add_argument("--file", dest="file_opt")

    pr = sub.add_parser("profile", help="manage sending profiles")
    pr.add_argument("action", choices=["add", "list", "show", "delete", "check"])
    pr.add_argument("name", nargs="?")
    pr.add_argument("--host")
    pr.add_argument("--port", type=int, default=587)
    pr.add_argument("--username")
    pr.add_argument("--password")
    pr.add_argument("--tls", default="starttls", choices=["starttls", "ssl", "none"])
    pr.add_argument("--from-name")
    pr.add_argument("--from-addr")
    pr.add_argument("--reply-to")
    pr.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    pr.add_argument("--batch", type=int, default=DEFAULT_BATCH)
    pr.add_argument("--xmailer", default="Microsoft Outlook 16.0")
    pr.add_argument("--url", help="tracking base URL for the TLS check")

    tp = sub.add_parser("template", help="manage email templates")
    tp.add_argument("action", choices=["add", "import", "list", "show", "delete",
                                       "generate", "categories"])
    tp.add_argument("name", nargs="?")
    tp.add_argument("--subject")
    tp.add_argument("--html")
    tp.add_argument("--file")
    tp.add_argument("--text-file")
    tp.add_argument("--attach", action="append")
    tp.add_argument("--all", action="store_true", help="generate the whole catalog")
    tp.add_argument("--category", help="generate one category only")
    tp.add_argument("--from-name", help="override the From display name")
    tp.add_argument("--cta", help="override the button label")
    tp.add_argument("--url", default="{{.URL}}", help="button URL (default {{.URL}})")

    ld = sub.add_parser("landing", help="manage landing pages")
    ld.add_argument("action", choices=["add", "mirror", "list", "show", "delete",
                                       "generate"])
    ld.add_argument("name", nargs="?")
    ld.add_argument("--url")
    ld.add_argument("--file")
    ld.add_argument("--redirect")
    ld.add_argument("--no-assets", action="store_true")
    ld.add_argument("--all", action="store_true", help="generate every variant")
    ld.add_argument("--brand", help="override the brand name")
    ld.add_argument("--title", help="override the page title")

    c = sub.add_parser("campaign", help="manage campaigns")
    c.add_argument("action", choices=["create", "list", "status", "add-targets",
                                      "send", "serve"])
    c.add_argument("name", nargs="?")
    c.add_argument("--profile")
    c.add_argument("--template")
    c.add_argument("--landing")
    c.add_argument("--url", default="http://127.0.0.1:8080")
    c.add_argument("--all", action="store_true")
    c.add_argument("--email", action="append")
    c.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    c.add_argument("--listen", default=DEFAULT_LISTEN)
    c.add_argument("--host")
    c.add_argument("--port", type=int, default=DEFAULT_PORT)

    pl = sub.add_parser("payload", help="generate stagers")
    pl.add_argument("--url", required=True)
    pl.add_argument("--title", default="Invoice")
    pl.add_argument("--iso", action="store_true")

    r = sub.add_parser("report", help="campaign report")
    r.add_argument("name")
    r.add_argument("--export")

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    handler = {
        "init": cmd_init, "seed": cmd_seed, "targets": cmd_targets,
        "profile": cmd_profile, "template": cmd_template, "landing": cmd_landing,
        "campaign": cmd_campaign, "payload": cmd_payload, "report": cmd_report,
    }.get(args.command)
    if not handler:
        return 1
    try:
        return handler(args)
    except KeyboardInterrupt:
        ui.line("interrupted", (C.YELLOW,))
        return 130
    except Exception as exc:
        ui.err(f"{exc.__class__.__name__}: {exc}")
        if os.environ.get("SPECTREPHISH_DEBUG"):
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
