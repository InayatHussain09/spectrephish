"""
SpectrePhish :: core/targets.py
CSV import/export with header aliasing.

Author : Inayat Hussain
"""

from __future__ import annotations

import csv
import os

from config import EXPORT_DIR

ALIASES = {
    "email": ("email", "e-mail", "mail", "email address", "address", "user", "username"),
    "first_name": ("first", "first_name", "firstname", "given name", "fname", "name"),
    "last_name": ("last", "last_name", "lastname", "surname", "lname"),
    "position": ("position", "title", "job", "role", "department", "dept"),
    "phone": ("phone", "mobile", "cell", "telephone", "tel"),
    "custom1": ("custom1", "custom_1", "group", "team"),
    "custom2": ("custom2", "custom_2", "location", "office"),
    "custom3": ("custom3", "custom_3", "manager"),
}


def _map_headers(fieldnames) -> dict:
    mapping = {}
    for raw in fieldnames or []:
        key = (raw or "").strip().lower()
        for canonical, options in ALIASES.items():
            if key in options and canonical not in mapping:
                mapping[raw] = canonical
    return mapping


def import_csv(store, path: str) -> tuple:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    added, skipped = 0, 0
    with open(path, newline="", encoding="utf-8-sig", errors="ignore") as handle:
        reader = csv.DictReader(handle)
        mapping = _map_headers(reader.fieldnames)
        if "email" not in mapping.values():
            raise ValueError("no email column found (expected one of: "
                             + ", ".join(ALIASES["email"]) + ")")
        before = {t["email"] for t in store.targets()}
        for row in reader:
            fields = {}
            email = None
            for raw, canonical in mapping.items():
                value = (row.get(raw) or "").strip()
                if canonical == "email":
                    email = value
                else:
                    fields[canonical] = value
            if not email or "@" not in email:
                skipped += 1
                continue
            store.upsert_target(email, **fields)
            if email.lower() not in before:
                added += 1
            else:
                skipped += 1
    return added, skipped


def export_csv(store, path: str | None = None) -> str:
    os.makedirs(EXPORT_DIR, exist_ok=True)
    path = path or os.path.join(EXPORT_DIR, "targets.csv")
    rows = store.targets()
    cols = ("email", "first_name", "last_name", "position", "phone",
            "custom1", "custom2", "custom3")
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(cols)
        for row in rows:
            writer.writerow([row.get(c, "") for c in cols])
    return path
