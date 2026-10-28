"""
SpectrePhish :: core/mailer.py
SMTP delivery with throttling and OPSEC-shaped headers.

Offensive logic: burst-sending is the #1 spam-filter trigger. Send with a
delay, set a plausible X-Mailer, and give Message-ID a domain that matches the
From address instead of leaking your relay hostname.

Author : Inayat Hussain
"""

from __future__ import annotations

import mimetypes
import os
import smtplib
import ssl
import time
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

from config import DEFAULT_TIMEOUT


class Mailer:
    def __init__(self, profile: dict, timeout: int = DEFAULT_TIMEOUT):
        self.p = profile
        self.timeout = timeout
        self.smtp = None
        self.sent = 0

    def connect(self) -> None:
        host = self.p["host"]
        port = int(self.p.get("port") or 587)
        tls = (self.p.get("tls") or "starttls").lower()

        if tls == "ssl":
            self.smtp = smtplib.SMTP_SSL(host, port, timeout=self.timeout,
                                         context=ssl.create_default_context())
        else:
            self.smtp = smtplib.SMTP(host, port, timeout=self.timeout)
            self.smtp.ehlo()
            if tls == "starttls":
                self.smtp.starttls(context=ssl.create_default_context())
                self.smtp.ehlo()

        if self.p.get("username"):
            self.smtp.login(self.p["username"], self.p.get("password") or "")

    def close(self) -> None:
        try:
            if self.smtp:
                self.smtp.quit()
        except Exception:
            pass

    def _build(self, to_addr: str, subject: str, html: str, text: str,
               attachments=None) -> EmailMessage:
        from_name = self.p.get("from_name") or ""
        from_addr = self.p.get("from_addr") or self.p.get("username") or ""
        domain = from_addr.split("@")[-1] if "@" in from_addr else None

        msg = EmailMessage()
        msg["From"] = f"{from_name} <{from_addr}>" if from_name else from_addr
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain=domain) if domain else make_msgid()

        if self.p.get("reply_to"):
            msg["Reply-To"] = self.p["reply_to"]
        if self.p.get("xmailer"):
            msg["X-Mailer"] = self.p["xmailer"]

        msg.set_content(text or "")
        if html:
            msg.add_alternative(html, subtype="html")

        for path in attachments or []:
            if not os.path.isfile(path):
                continue
            ctype, _ = mimetypes.guess_type(path)
            maintype, _, subtype = (ctype or "application/octet-stream").partition("/")
            with open(path, "rb") as handle:
                msg.add_attachment(handle.read(), maintype=maintype, subtype=subtype,
                                   filename=os.path.basename(path))
        return msg

    def send(self, to_addr: str, subject: str, html: str, text: str,
             attachments=None) -> bool:
        msg = self._build(to_addr, subject, html, text, attachments)
        try:
            self.smtp.send_message(msg)
        except smtplib.SMTPServerDisconnected:
            self.connect()
            self.smtp.send_message(msg)
        self.sent += 1
        delay = float(self.p.get("delay") or 0)
        if delay:
            time.sleep(delay)
        return True
