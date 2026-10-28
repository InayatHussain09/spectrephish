"""
SpectrePhish :: core/store.py
SQLite persistence for targets, profiles, templates, landings, campaigns, events.

Author : Inayat Hussain
"""

from __future__ import annotations

import json
import os
import secrets
import sqlite3
import time

from config import STORE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT, last_name TEXT, position TEXT, phone TEXT,
    custom1 TEXT, custom2 TEXT, custom3 TEXT,
    created REAL
);
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    host TEXT, port INTEGER, username TEXT, password TEXT,
    tls TEXT DEFAULT 'starttls',
    from_name TEXT, from_addr TEXT, reply_to TEXT,
    delay REAL DEFAULT 1.0, batch INTEGER DEFAULT 25,
    xmailer TEXT DEFAULT 'Microsoft Outlook 16.0',
    created REAL
);
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    subject TEXT, html TEXT, text TEXT, attachments TEXT, created REAL
);
CREATE TABLE IF NOT EXISTS landings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    html TEXT, capture TEXT, redirect_url TEXT,
    redirect_on_submit INTEGER DEFAULT 1, created REAL
);
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    profile_id INTEGER, template_id INTEGER, landing_id INTEGER,
    url_base TEXT, status TEXT DEFAULT 'created', created REAL, launched REAL
);
CREATE TABLE IF NOT EXISTS campaign_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER, target_id INTEGER,
    token TEXT UNIQUE, email TEXT,
    sent INTEGER DEFAULT 0, opened INTEGER DEFAULT 0, clicked INTEGER DEFAULT 0,
    submitted INTEGER DEFAULT 0, reported INTEGER DEFAULT 0,
    first_open REAL, first_click REAL, first_submit REAL,
    ua TEXT, ip TEXT, captured TEXT
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER, token TEXT, kind TEXT, ts REAL, meta TEXT
);
"""


def now() -> float:
    return time.time()


def new_token() -> str:
    return secrets.token_hex(8)


class Store:
    def __init__(self, path: str = STORE_PATH):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA)
        self.db.commit()

    def _exec(self, sql: str, args=()):
        cur = self.db.execute(sql, args)
        self.db.commit()
        return cur

    def _rows(self, sql: str, args=()):
        return [dict(r) for r in self.db.execute(sql, args).fetchall()]

    def _row(self, sql: str, args=()):
        rows = self._rows(sql, args)
        return rows[0] if rows else None

    # ---------------- targets ----------------
    def upsert_target(self, email: str, **fields) -> int:
        email = email.strip().lower()
        existing = self._row("SELECT id FROM targets WHERE email=?", (email,))
        if existing:
            return existing["id"]
        cur = self._exec(
            "INSERT INTO targets (email, first_name, last_name, position, phone,"
            " custom1, custom2, custom3, created) VALUES (?,?,?,?,?,?,?,?,?)",
            (email, fields.get("first_name", ""), fields.get("last_name", ""),
             fields.get("position", ""), fields.get("phone", ""),
             fields.get("custom1", ""), fields.get("custom2", ""),
             fields.get("custom3", ""), now()))
        return cur.lastrowid

    def targets(self) -> list:
        return self._rows("SELECT * FROM targets ORDER BY id")

    def delete_target(self, tid: int) -> None:
        self._exec("DELETE FROM targets WHERE id=?", (tid,))

    # ---------------- profiles ----------------
    def upsert_profile(self, name: str, **f) -> int:
        row = self._row("SELECT id FROM profiles WHERE name=?", (name,))
        cols = ("host", "port", "username", "password", "tls", "from_name",
                "from_addr", "reply_to", "delay", "batch", "xmailer")
        values = [f.get(c, "") for c in cols]
        if row:
            sets = ", ".join(f"{c}=?" for c in cols)
            self._exec(f"UPDATE profiles SET {sets} WHERE id=?", values + [row["id"]])
            return row["id"]
        placeholders = ",".join("?" * (len(cols) + 2))
        cur = self._exec(
            f"INSERT INTO profiles (name,{','.join(cols)},created) VALUES ({placeholders})",
            [name] + values + [now()])
        return cur.lastrowid

    def profiles(self) -> list:
        return self._rows("SELECT * FROM profiles ORDER BY id")

    def profile(self, pid: int):
        return self._row("SELECT * FROM profiles WHERE id=?", (pid,))

    def profile_by_name(self, name: str):
        return self._row("SELECT * FROM profiles WHERE name=?", (name,))

    # ---------------- templates ----------------
    def upsert_template(self, name: str, subject: str, html: str,
                        text: str = "", attachments=None) -> int:
        row = self._row("SELECT id FROM templates WHERE name=?", (name,))
        att = json.dumps(attachments or [])
        if row:
            self._exec("UPDATE templates SET subject=?,html=?,text=?,attachments=? WHERE id=?",
                       (subject, html, text, att, row["id"]))
            return row["id"]
        cur = self._exec(
            "INSERT INTO templates (name,subject,html,text,attachments,created)"
            " VALUES (?,?,?,?,?,?)", (name, subject, html, text, att, now()))
        return cur.lastrowid

    def templates(self) -> list:
        return self._rows("SELECT * FROM templates ORDER BY id")

    def template(self, tid: int):
        return self._row("SELECT * FROM templates WHERE id=?", (tid,))

    def template_by_name(self, name: str):
        return self._row("SELECT * FROM templates WHERE name=?", (name,))

    # ---------------- landings ----------------
    def upsert_landing(self, name: str, html: str, capture=None,
                       redirect_url: str = "", redirect_on_submit: bool = True) -> int:
        row = self._row("SELECT id FROM landings WHERE name=?", (name,))
        cap = json.dumps(capture or [])
        if row:
            self._exec("UPDATE landings SET html=?,capture=?,redirect_url=?,"
                       "redirect_on_submit=? WHERE id=?",
                       (html, cap, redirect_url, int(redirect_on_submit), row["id"]))
            return row["id"]
        cur = self._exec(
            "INSERT INTO landings (name,html,capture,redirect_url,redirect_on_submit,created)"
            " VALUES (?,?,?,?,?,?)",
            (name, html, cap, redirect_url, int(redirect_on_submit), now()))
        return cur.lastrowid

    def landings(self) -> list:
        return self._rows("SELECT * FROM landings ORDER BY id")

    def landing(self, lid: int):
        return self._row("SELECT * FROM landings WHERE id=?", (lid,))

    def landing_by_name(self, name: str):
        return self._row("SELECT * FROM landings WHERE name=?", (name,))

    def landing_url(self, cid: int) -> str:
        row = self._row(
            "SELECT l.redirect_url FROM campaigns c LEFT JOIN landings l"
            " ON l.id=c.landing_id WHERE c.id=?", (cid,))
        return (row or {}).get("redirect_url") or ""

    # ---------------- campaigns ----------------
    def create_campaign(self, name: str, profile_id: int, template_id: int,
                        landing_id: int, url_base: str) -> int:
        cur = self._exec(
            "INSERT INTO campaigns (name,profile_id,template_id,landing_id,url_base,created)"
            " VALUES (?,?,?,?,?,?)",
            (name, profile_id, template_id, landing_id, url_base.rstrip("/"), now()))
        return cur.lastrowid

    def campaigns(self) -> list:
        return self._rows("SELECT * FROM campaigns ORDER BY id DESC")

    def campaign(self, cid: int):
        return self._row("SELECT * FROM campaigns WHERE id=?", (cid,))

    def campaign_by_name(self, name: str):
        return self._row("SELECT * FROM campaigns WHERE name=?", (name,))

    def set_status(self, cid: int, status: str) -> None:
        if status == "running":
            self._exec("UPDATE campaigns SET status=?, launched=? WHERE id=?",
                       (status, now(), cid))
        else:
            self._exec("UPDATE campaigns SET status=? WHERE id=?", (status, cid))

    def add_campaign_targets(self, cid: int, target_ids: list) -> int:
        added = 0
        for tid in target_ids:
            t = self._row("SELECT * FROM targets WHERE id=?", (tid,))
            if not t:
                continue
            try:
                self._exec(
                    "INSERT INTO campaign_targets (campaign_id,target_id,token,email)"
                    " VALUES (?,?,?,?)", (cid, tid, new_token(), t["email"]))
                added += 1
            except sqlite3.IntegrityError:
                continue
        return added

    def campaign_targets(self, cid: int) -> list:
        return self._rows("SELECT * FROM campaign_targets WHERE campaign_id=? ORDER BY id", (cid,))

    def campaign_target(self, cid: int, token: str):
        return self._row("SELECT * FROM campaign_targets WHERE campaign_id=? AND token=?",
                         (cid, token))

    def target_by_token(self, token: str):
        return self._row(
            "SELECT ct.*, t.first_name, t.last_name, t.position "
            "FROM campaign_targets ct JOIN targets t ON t.id=ct.target_id "
            "WHERE ct.token=?", (token,))

    def mark(self, cid: int, token: str, kind: str) -> None:
        col = {"sent": "sent", "open": "opened", "click": "clicked",
               "submit": "submitted", "report": "reported"}.get(kind)
        if not col:
            return
        stamp = {"open": "first_open", "click": "first_click",
                 "submit": "first_submit"}.get(kind)
        if stamp:
            self._exec(
                f"UPDATE campaign_targets SET {col}=1, {stamp}=COALESCE({stamp},?)"
                f" WHERE campaign_id=? AND token=?", (now(), cid, token))
        else:
            self._exec(
                f"UPDATE campaign_targets SET {col}=1 WHERE campaign_id=? AND token=?",
                (cid, token))

    def note(self, cid: int, token: str, kind: str, meta: dict | None = None) -> None:
        self._exec("INSERT INTO events (campaign_id,token,kind,ts,meta) VALUES (?,?,?,?,?)",
                   (cid, token, kind, now(), json.dumps(meta or {})))

    def events(self, cid: int, limit: int = 200) -> list:
        return self._rows("SELECT * FROM events WHERE campaign_id=? ORDER BY id DESC LIMIT ?",
                          (cid, limit))

    def set_client_info(self, cid: int, token: str, ua: str, ip: str) -> None:
        self._exec("UPDATE campaign_targets SET ua=?, ip=? WHERE campaign_id=? AND token=?",
                   (ua, ip, cid, token))

    def save_capture(self, cid: int, token: str, data: dict) -> None:
        self._exec("UPDATE campaign_targets SET captured=? WHERE campaign_id=? AND token=?",
                   (json.dumps(data), cid, token))

    def stats(self, cid: int) -> dict:
        row = self._row(
            "SELECT COUNT(*) total, SUM(sent) sent, SUM(opened) opened,"
            " SUM(clicked) clicked, SUM(submitted) submitted, SUM(reported) reported"
            " FROM campaign_targets WHERE campaign_id=?", (cid,))
        return {k: (row[k] or 0) for k in
                ("total", "sent", "opened", "clicked", "submitted", "reported")}

    def campaign_for_token(self, token: str):
        return self._row("SELECT * FROM campaign_targets WHERE token=?", (token,))
