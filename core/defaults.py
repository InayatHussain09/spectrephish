"""
SpectrePhish :: core/defaults.py
Built-in catalog: 60 email templates + 20 landing variants.

Design: every entry is METADATA ONLY. core/generate.py expands it into a full
responsive HTML email or login page. You supply from/subject/CTA and the
template does the rest -- no HTML editing, ever.

Author : Inayat Hussain
"""

from __future__ import annotations

EMAIL_FIELDS = ("name", "category", "brand", "accent", "from_name", "subject",
                "preheader", "headline", "body", "cta", "footer")

_EMAIL_RAW = """
# name | category | brand | accent | from_name | subject | preheader | headline | body(~ separated) | cta | footer
m365-password-expiry|Credential|Microsoft 365|#0067b8|IT Service Desk|Action required: Your password expires in 24 hours|Re-authenticate to avoid losing access|Your password expires in 24 hours|Hi {{.FirstName}},~Your {{.Domain}} account password expires in 24 hours.~Re-authenticate now to avoid losing access to your mailbox and files.|Keep my access|Automated message from {{.Domain}} IT Services
m365-mfa-reset|Credential|Microsoft 365|#0067b8|Microsoft Account|Multi-factor authentication has been reset|Re-enroll your authenticator|Your MFA was reset|Hi {{.FirstName}},~Multi-factor authentication on your account was reset by an administrator.~Re-enroll your authenticator app to restore full access.|Re-enroll now|Microsoft 365 · {{.Domain}}
m365-storage-quota|IT Notice|Microsoft 365|#0078d4|Microsoft 365|Your mailbox is almost full|95% of your storage is used|Mailbox storage almost full|Hi {{.FirstName}},~Your mailbox is at 95% of its {{.Domain}} quota.~Once full you will stop receiving new mail.|Increase my quota|Manage storage in Outlook
m365-new-signin|Security|Microsoft 365|#0078d4|Microsoft Account Team|New sign-in to your account|Was this you?|New sign-in detected|Hi {{.FirstName}},~We detected a new sign-in to your account from an unrecognised device.~If this was not you, secure your account now.|Secure my account|Microsoft Account · {{.Domain}}
sharepoint-share|Document|SharePoint|#0364b8|SharePoint Online|{{.Sender}} shared a document with you|A file was shared with you|A document was shared with you|Hi {{.FirstName}},~A file was shared with you on {{.Domain}} SharePoint.~Open it to review and collaborate.|Open document|SharePoint Online
onedrive-share|Document|OneDrive|#0364b8|OneDrive|{{.Sender}} shared "Q4 Report.xlsx" with you|Open the shared workbook|A file was shared with you|Hi {{.FirstName}},~"Q4 Report.xlsx" was shared with you via OneDrive.~Sign in to view the file.|Open in OneDrive|OneDrive for Business
google-workspace-password|Credential|Google Workspace|#1a73e8|Google Workspace|Your password will expire soon|Update your password|Your password expires soon|Hi {{.FirstName}},~The password for your {{.Domain}} Google Workspace account will expire in 3 days.~Update it to stay signed in.|Update password|Google Workspace
google-drive-share|Document|Google Drive|#1a73e8|Google Drive|{{.Sender}} shared a file with you|Open the shared file|A file was shared with you|Hi {{.FirstName}},~A document was shared with you on Google Drive.~Click below to open it.|Open in Drive|Google Drive · {{.Domain}}
okta-sso-verify|Credential|Okta|#007dc1|Okta|Verify your identity|Complete single sign-on setup|Verify your identity|Hi {{.FirstName}},~Your organisation has enabled a new sign-in flow for {{.Domain}} applications.~Verify your identity to continue.|Verify identity|Okta Identity Cloud
okta-mfa-enroll|Credential|Okta|#007dc1|Okta|Action required: Enroll in MFA|Set up your second factor|Enroll in multi-factor auth|Hi {{.FirstName}},~Multi-factor authentication is now mandatory for {{.Domain}} applications.~Enroll a device to keep access.|Enroll device|Okta Identity Cloud
vpn-cert-renewal|IT Notice|Corporate VPN|#2b579a|IT Infrastructure|VPN certificate expires in 48 hours|Renew before you lose access|VPN certificate expiring|Hi {{.FirstName}},~Your {{.Domain}} VPN certificate expires in 48 hours.~Renew it to avoid losing remote access.|Renew certificate|IT Infrastructure Team
vpn-credential-expiry|Credential|Corporate VPN|#2b579a|IT Infrastructure|VPN credentials expiring|Update your VPN password|VPN credentials expiring|Hi {{.FirstName}},~Your remote access credentials for {{.Domain}} expire in 2 days.~Update them to stay connected.|Update VPN password|IT Infrastructure Team
webmail-quota-full|IT Notice|Webmail|#444444|Postmaster|Your mailbox has exceeded its quota|Free space to keep receiving mail|Mailbox quota exceeded|Hi {{.FirstName}},~Your {{.Domain}} mailbox has exceeded its quota.~New messages are being rejected until you free space.|Manage mailbox|Postmaster · {{.Domain}}
citrix-session-timeout|IT Notice|Citrix|#464646|Citrix Gateway|Your session will expire|Reconnect to your workspace|Session expiring|Hi {{.FirstName}},~Your Citrix session has been idle and will expire shortly.~Reconnect to resume your applications.|Reconnect|Citrix Workspace
docusign-signature|Document|DocuSign|#1a3c6e|DocuSign|Please sign: Contract 2026-114|Signature required before Friday|Signature required|Hi {{.FirstName}},~A document is awaiting your signature on DocuSign.~Please review and sign before the deadline.|Review and sign|DocuSign
adobe-sign|Document|Adobe Acrobat Sign|#fa0f00|Adobe Acrobat Sign|Signature requested: Onboarding pack|Sign to complete onboarding|Signature requested|Hi {{.FirstName}},~An onboarding document is awaiting your signature.~Complete it to finalise your records.|Sign document|Adobe Acrobat Sign
dropbox-share|Document|Dropbox|#0061ff|Dropbox|{{.Sender}} shared a folder with you|Open the shared folder|A folder was shared with you|Hi {{.FirstName}},~A folder was shared with you on Dropbox.~Open it to view the contents.|Open folder|Dropbox Business
box-share|Document|Box|#0061d5|Box|New file shared with you|Open the file on Box|A file was shared with you|Hi {{.FirstName}},~A file was shared with you on Box.~Sign in to view it.|Open on Box|Box · {{.Domain}}
invoice-attached|Finance|Accounts Payable|#0f766e|Accounts Payable|Invoice INV-2026-0412 attached|Review and approve|Invoice attached|Hi {{.FirstName}},~Please find attached invoice INV-2026-0412 for {{.Domain}}.~Kindly review and approve at your earliest convenience.|View invoice|Accounts Payable
purchase-order|Finance|Procurement|#0f766e|Procurement|Purchase order PO-88421 for approval|Approve to proceed|PO awaiting approval|Hi {{.FirstName}},~Purchase order PO-88421 requires your approval.~Approve to keep the delivery on schedule.|Approve PO|Procurement Team
remittance-advice|Finance|Finance|#166534|Finance Department|Remittance advice - payment processed|Payment confirmation|Payment processed|Hi {{.FirstName}},~A payment has been processed and the remittance advice is ready.~View the details below.|View remittance|Finance Department
payroll-notification|HR|Payroll|#7c3aed|Payroll|Your payslip is ready|View this month's payslip|Payslip available|Hi {{.FirstName}},~Your payslip for this period is now available.~Sign in to download it.|View payslip|Payroll · {{.Domain}}
expense-reimbursement|Finance|Expenses|#0f766e|Expenses|Expense claim approved|Reimbursement scheduled|Expense approved|Hi {{.FirstName}},~Your expense claim has been approved.~The reimbursement will be processed in the next run.|View claim|Expenses Team
tax-document|Finance|Finance|#166534|Finance|Your tax document is ready|Download before the deadline|Tax document ready|Hi {{.FirstName}},~Your annual tax document is available for download.~Please retrieve it before the filing deadline.|Download document|Finance Department
bank-statement|Finance|Banking|#0b3d91|Online Banking|Your statement is ready|View your latest statement|Statement available|Hi {{.FirstName}},~Your latest account statement is ready to view.~Sign in to download the PDF.|View statement|Online Banking
quickbooks-invoice|Finance|QuickBooks|#2ca01c|QuickBooks|Invoice from {{.Domain}}|Payment due in 7 days|New invoice|Hi {{.FirstName}},~A new invoice has been issued to your account.~Payment is due within 7 days.|View invoice|QuickBooks Online
stripe-payment-failed|Finance|Stripe|#635bff|Stripe|Payment failed - action required|Update your payment method|Payment failed|Hi {{.FirstName}},~A recent payment on your {{.Domain}} account failed.~Update your payment method to avoid interruption.|Update payment method|Stripe
benefits-enrollment|HR|Benefits|#7c3aed|HR Benefits|Open enrollment closes Friday|Enroll or lose coverage|Open enrollment closing|Hi {{.FirstName}},~The {{.Domain}} benefits enrollment window closes Friday.~Review your options and confirm your elections.|Enroll now|HR Benefits Team
policy-update|HR|Human Resources|#7c3aed|Human Resources|Updated policy - acknowledgement required|Please acknowledge|Policy acknowledgement|Hi {{.FirstName}},~The {{.Domain}} remote-work policy has been updated.~Please read and acknowledge by the end of the week.|Acknowledge policy|Human Resources
payslip-available|HR|Payroll|#7c3aed|Payroll|Payslip available for download|Now in the employee portal|Payslip ready|Hi {{.FirstName}},~Your latest payslip is available in the employee portal.~Download it at your convenience.|Open portal|Payroll · {{.Domain}}
performance-review|HR|Human Resources|#7c3aed|Human Resources|Your performance review is due|Complete by Friday|Review due|Hi {{.FirstName}},~Your quarterly self-review is due this Friday.~Complete it in the portal to keep the cycle on track.|Start review|Human Resources
holiday-calendar|HR|Human Resources|#7c3aed|Human Resources|Holiday calendar updated|Check the new dates|Calendar updated|Hi {{.FirstName}},~The {{.Domain}} holiday calendar has been updated for the coming year.~Review the new dates.|View calendar|Human Resources
mandatory-training|HR|Learning|#7c3aed|Learning and Development|Mandatory security training|Complete before month end|Training assigned|Hi {{.FirstName}},~A mandatory security awareness module has been assigned to you.~Complete it before month end.|Start training|Learning and Development
hr-onboarding|HR|Human Resources|#7c3aed|HR Onboarding|Complete your onboarding documents|Finish before day one|Onboarding documents|Hi {{.FirstName}},~Welcome to {{.Domain}}.~Please complete your onboarding documents before your first day.|Complete onboarding|HR Onboarding
mailbox-full|IT Notice|Exchange|#0078d4|Postmaster|Mailbox full - mail delayed|Free space now|Mailbox full|Hi {{.FirstName}},~Your mailbox is full and incoming mail is being delayed.~Free space or increase your quota.|Manage mailbox|Postmaster · {{.Domain}}
software-update|IT Notice|IT|#334155|IT Service Desk|Mandatory software update|Install before Friday|Update required|Hi {{.FirstName}},~A mandatory security update must be installed on your workstation.~Schedule it before Friday.|Start update|IT Service Desk
antivirus-renewal|IT Notice|IT Security|#334155|IT Security|Endpoint protection licence expiring|Renew to stay protected|Licence expiring|Hi {{.FirstName}},~Your endpoint protection licence expires in 5 days.~Renew it to stay compliant.|Renew licence|IT Security
device-quarantine|Security|IT Security|#b91c1c|IT Security|Your device has been quarantined|Restore network access|Device quarantined|Hi {{.FirstName}},~Your device failed a compliance check and has been quarantined.~Remediate to restore network access.|Restore access|IT Security
suspicious-signin|Security|Security|#b91c1c|Security Team|Suspicious sign-in attempt|Verify it was you|Suspicious sign-in|Hi {{.FirstName}},~We blocked a suspicious sign-in to your {{.Domain}} account.~Confirm whether it was you.|Review activity|Security Team
password-breach|Security|Security|#b91c1c|Security Team|Your password appeared in a breach|Reset it now|Password breached|Hi {{.FirstName}},~Your {{.Domain}} password was found in a public data breach.~Reset it immediately to stay safe.|Reset password|Security Team
teams-message|Collab|Microsoft Teams|#5059c9|Microsoft Teams|You have unread messages|Reply in Teams|New messages|Hi {{.FirstName}},~You have unread messages waiting in Microsoft Teams.~Open the conversation to reply.|Open Teams|Microsoft Teams
zoom-invite|Collab|Zoom|#2d8cff|Zoom|Meeting invitation: All-hands|Join on Thursday 10:00|Meeting invitation|Hi {{.FirstName}},~You are invited to the {{.Domain}} all-hands on Thursday at 10:00.~Join using the link below.|Join meeting|Zoom
calendar-invite|Collab|Calendar|#2563eb|Calendar|Invitation: Budget review|Accept or decline|Calendar invitation|Hi {{.FirstName}},~You have been invited to the quarterly budget review.~Please accept or decline.|Respond to invite|Calendar
webex-recording|Collab|Webex|#0f6cbd|Webex|Your recording is ready|Watch the session|Recording ready|Hi {{.FirstName}},~The recording of your recent Webex session is ready to view.~It expires in 30 days.|Watch recording|Webex
slack-invite|Collab|Slack|#4a154b|Slack|You have been invited to a workspace|Join {{.Domain}} on Slack|Workspace invitation|Hi {{.FirstName}},~You have been invited to join the {{.Domain}} workspace on Slack.~Accept the invitation to get started.|Join workspace|Slack
voicemail|Misc|Voicemail|#475569|Voicemail System|New voicemail from +1 555 0134|Listen to the message|New voicemail|Hi {{.FirstName}},~You received a voicemail from +1 555 0134.~It is 42 seconds long and will expire in 7 days.|Listen to voicemail|Voicemail System
fax-received|Misc|Fax Service|#475569|Fax Service|New fax received|View the document|Fax received|Hi {{.FirstName}},~A new fax has been received on your {{.Domain}} number.~View the attached document.|View fax|Fax Service
scanned-document|Misc|Office Scanner|#475569|Office Scanner|Scanned document from copier|View the scan|Scanned document|Hi {{.FirstName}},~A document was scanned to your mailbox from the office copier.~Open the attachment to view it.|View scan|Office Scanner
fedex-delivery|Shipping|FedEx|#4d148c|FedEx|Your parcel is out for delivery|Track your shipment|Out for delivery|Hi {{.FirstName}},~Your parcel is out for delivery and will arrive today.~Track it for the latest status.|Track parcel|FedEx
dhl-shipment|Shipping|DHL Express|#d40511|DHL Express|Shipment notification|Your parcel has shipped|Shipment on the way|Hi {{.FirstName}},~Your shipment has left our facility and is on the way.~Track it for delivery updates.|Track shipment|DHL Express
ups-package|Shipping|UPS|#351c15|UPS|Delivery attempt scheduled|Reschedule or track|Delivery scheduled|Hi {{.FirstName}},~A delivery attempt is scheduled for your package.~Track it to see the window.|Track package|UPS
amazon-order|Shipping|Amazon|#232f3e|Amazon|Your order has been dispatched|Track your delivery|Order dispatched|Hi {{.FirstName}},~Your recent order has been dispatched.~Track it for the delivery estimate.|Track order|Amazon
survey-feedback|Misc|Employee Experience|#0ea5e9|Employee Experience|Quick 2-minute survey|Share your feedback|Short survey|Hi {{.FirstName}},~We would value your feedback on the recent {{.Domain}} changes.~The survey takes two minutes.|Take survey|Employee Experience
subscription-renewal|Finance|Subscriptions|#0ea5e9|Subscriptions|Your subscription renews soon|Review before it renews|Subscription renewing|Hi {{.FirstName}},~Your {{.Domain}} subscription renews in 7 days.~Review the plan before it charges.|Manage subscription|Subscriptions
license-expiry|IT Notice|IT Licensing|#334155|IT Licensing|Software licence expiring|Renew before month end|Licence expiring|Hi {{.FirstName}},~A software licence assigned to you expires at month end.~Renew to avoid losing access.|Renew licence|IT Licensing
conference-registration|Misc|Events|#7c3aed|Events|Confirm your conference place|Registration closes Friday|Confirm your place|Hi {{.FirstName}},~Your place at the {{.Domain}} conference is held provisionally.~Confirm it before Friday.|Confirm place|Events Team
newsletter-confirm|Misc|Communications|#0ea5e9|Communications|Confirm your subscription|One click to stay subscribed|Confirm subscription|Hi {{.FirstName}},~Please confirm your subscription to continue receiving {{.Domain}} updates.~One click is all it takes.|Confirm subscription|Communications
wifi-guest|IT Notice|Network Team|#334155|Network Team|Guest WiFi credentials|Connect with your email|Guest WiFi access|Hi {{.FirstName}},~Guest WiFi access has been provisioned for you.~Sign in with your {{.Domain}} email to connect.|Connect to WiFi|Network Team
printer-queue|IT Notice|Print Services|#334155|Print Services|Your print job is held|Release it at the printer|Print job held|Hi {{.FirstName}},~A print job is held in the secure queue under your account.~Release it at the printer.|Release job|Print Services
shared-mailbox|IT Notice|Exchange|#0078d4|IT Service Desk|Shared mailbox access granted|Accept the invitation|Mailbox access granted|Hi {{.FirstName}},~You have been granted access to a shared {{.Domain}} mailbox.~Accept the invitation to add it to Outlook.|Accept invitation|IT Service Desk
"""

LANDING_FIELDS = ("name", "brand", "accent", "title", "subtitle", "logo",
                  "button", "mode")

_LANDING_RAW = """
# name | brand | accent | title | subtitle | logo | button | mode(password|mfa|sso|cert)
m365|Microsoft 365|#0067b8|Sign in|to continue to Outlook|Microsoft|Sign in|password
owa|Outlook Web|#0078d4|Sign in|to your mailbox|Outlook|Sign in|password
google|Google Workspace|#1a73e8|Sign in|to continue to Gmail|Google|Next|password
okta|Okta|#007dc1|Sign in|to your organisation|okta|Sign in|password
sso-generic|Corporate SSO|#2563eb|Sign in|Single sign-on|SSO|Continue|password
vpn|Corporate VPN|#2b579a|VPN Login|Remote access portal|VPN|Connect|password
webmail|Webmail|#444444|Webmail Login|Company mail|Webmail|Log in|password
citrix|Citrix Gateway|#464646|Sign in|to your workspace|Citrix|Log on|password
docusign|DocuSign|#1a3c6e|Sign in|to sign your document|DocuSign|Sign in|password
adobe|Adobe Acrobat Sign|#fa0f00|Sign in|to review documents|Adobe|Sign in|password
dropbox|Dropbox|#0061ff|Sign in|to view the shared folder|Dropbox|Continue|password
sharepoint|SharePoint|#0364b8|Sign in|to access the document|SharePoint|Sign in|password
payroll|Payroll Portal|#7c3aed|Employee Login|Payslips and benefits|Payroll|Sign in|password
hr-portal|HR Portal|#7c3aed|HR Portal Login|Employee self-service|HR|Sign in|password
bank|Online Banking|#0b3d91|Online Banking|Personal and business|Bank|Log in|password
duo|Duo Security|#6bbf59|Two-Factor Authentication|Enter your passcode|Duo|Verify|mfa
mfa-code|Microsoft 365|#0067b8|Verify your identity|Enter the code from your authenticator|Microsoft|Verify|mfa
password-reset|Microsoft 365|#0067b8|Reset password|Choose a new password|Microsoft|Reset|password
cert-login|Corporate SSO|#2563eb|Certificate Login|Smartcard or certificate|SSO|Continue|cert
guest-wifi|Guest Network|#334155|Guest Network|Sign in to connect|WiFi|Connect|sso
"""


def _parse(raw: str, fields: tuple) -> list:
    out = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        parts += [""] * (len(fields) - len(parts))
        spec = dict(zip(fields, parts[: len(fields)]))
        body = spec.get("body", "")
        spec["body"] = [s.strip() for s in body.split("~") if s.strip()]
        out.append(spec)
    return out


EMAIL_TEMPLATES = _parse(_EMAIL_RAW, EMAIL_FIELDS)
LANDING_TEMPLATES = _parse(_LANDING_RAW, LANDING_FIELDS)

EMAIL_INDEX = {t["name"]: t for t in EMAIL_TEMPLATES}
LANDING_INDEX = {t["name"]: t for t in LANDING_TEMPLATES}


def email_names() -> list:
    return list(EMAIL_INDEX)


def landing_names() -> list:
    return list(LANDING_INDEX)


def email_spec(name: str):
    return EMAIL_INDEX.get(name)


def landing_spec(name: str):
    return LANDING_INDEX.get(name)


def categories() -> list:
    seen = []
    for t in EMAIL_TEMPLATES:
        if t["category"] not in seen:
            seen.append(t["category"])
    return sorted(seen)
