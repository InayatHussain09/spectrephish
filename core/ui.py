"""
SpectrePhish :: core/ui.py
Presentation layer. Violet accent, dim structure, colour for meaning.

Author : Inayat Hussain
"""

from __future__ import annotations

import sys

from config import BANNER, BANNER_META, C, paint

WIDTH = 76


def _fit(text, width: int) -> str:
    text = str(text)
    if len(text) <= width:
        return text
    return text[: max(0, width - 3)] + "..."


def banner() -> None:
    print(paint(BANNER, C.ACCENT))
    for i, meta in enumerate(BANNER_META):
        if not meta:
            print()
        elif i == 0:
            print(paint("        " + meta, C.WHITE, C.BOLD))
        elif i == 1:
            print(paint("        " + meta, C.ACCENT2))
        else:
            print(paint("        " + meta, C.GREY))


def phase(index: int, total: int, text: str) -> None:
    label = f" {index:02d} / {total:02d} · {text.upper()} "
    print()
    print(paint("┃", C.ACCENT) + paint(label, C.BOLD, C.WHITE)
          + paint("─" * max(0, WIDTH - len(label) - 2), C.DIMC))


def section(text: str) -> None:
    head = f"─ {text} "
    print(paint("╭" + head + "─" * max(0, WIDTH - len(head) - 1), C.DIMC))


def end_section() -> None:
    print(paint("╰" + "─" * (WIDTH - 1), C.DIMC))


def kv(pairs) -> None:
    for key, value in pairs:
        print(f"│  {paint(str(key).ljust(13), C.GREY)} {_fit(value, WIDTH - 18)}")


def line(text: str, color=None) -> None:
    print(f"   {paint(text, *(color or ()))}")


def bullet(text: str, color=None) -> None:
    print(f"     {paint('·', C.DIMC)} {paint(text, *(color or ()))}")


def ok(text: str) -> None:
    print(f"   {paint('▸', C.GREEN)} {paint(text, C.WHITE)}")


def warn(text: str) -> None:
    print(f"   {paint('▸', C.YELLOW)} {paint(text, C.YELLOW)}")


def err(text: str) -> None:
    print(f"   {paint('▸', C.RED)} {paint(text, C.RED)}")


def table(headers, rows, widths=None) -> None:
    if not rows:
        line("(empty)", (C.DIMC,))
        return
    cols = len(headers)
    widths = widths or [max(len(str(h)), *(len(str(r[i])) for r in rows)) + 2
                        for i, h in enumerate(headers)]
    head = "   " + "".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
    print(paint(head, C.BOLD, C.WHITE))
    print("   " + paint("─" * sum(widths), C.DIMC))
    for row in rows:
        cells = "".join(_fit(str(c), widths[i] - 1).ljust(widths[i])
                        for i, c in enumerate(row[:cols]))
        print("   " + paint(cells, C.GREY))


def progress(done: int, total: int, label: str = "", extra: str = "") -> None:
    total = max(total, 1)
    pct = min(100, int(done * 100 / total))
    filled = int(pct * 28 / 100)
    bar = paint("█" * filled, C.ACCENT) + paint("░" * (28 - filled), C.DIMC)
    tail = f" {pct:3d}%  {label} {extra}"
    sys.stdout.write(f"\r   [{bar}]{_fit(tail, WIDTH - 36)}")
    sys.stdout.flush()
    if done >= total:
        sys.stdout.write("\n")


def card(title: str, pairs) -> None:
    tag = f"─ {title} "
    print()
    print(paint("╭" + tag + "─" * max(0, WIDTH - len(tag) - 1), C.DIMC))
    for key, value in pairs:
        print(f"│  {paint(str(key).ljust(12), C.GREY)} {_fit(value, WIDTH - 17)}")
    print(paint("╰" + "─" * (WIDTH - 1), C.DIMC))
