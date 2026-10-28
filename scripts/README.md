# SpectrePhish

### Phishing Operator Framework — Campaigns · Tracking · OPSEC

**SpectrePhish** is a CLI-based phishing simulation framework designed as an alternative to GoPhish, with a focus on operational security (OPSEC), email infrastructure validation, campaign attribution, and tracking reliability.

Built by **Inayat Hussain** — Red Team Operator & Offensive Security Engineer.

`Campaign Management` · `Email Templates` · `Attribution` · `OPSEC Preflight`

---

## Overview

SpectrePhish brings phishing simulation workflows into a command-line interface, combining campaign preparation, email template generation, landing-page customization, recipient-level attribution, and infrastructure preflight checks.

Unlike conventional phishing simulation platforms, SpectrePhish emphasizes operational visibility and tracking reliability, including email authentication checks, transport security validation, header hygiene, and heuristics for identifying automated email opens.

The goal is to help authorized security teams conduct controlled phishing assessments with better visibility into campaign delivery and tracking behavior.

## Features

- **60 Built-in Email Templates** — Generate campaign emails from structured metadata without manually editing HTML.
- **20 Landing-Page Variants** — Select from predefined landing-page designs for different simulation scenarios.
- **Real-Site Landing Mirroring** — Mirror authorized test pages with inlined assets for controlled simulation environments.
- **Per-Target Attribution** — Generate unique tracking tokens to associate campaign interactions with individual test recipients.
- **OPSEC Preflight Engine** — Check SPF, DMARC, TLS, SMTP reachability, and email header hygiene before campaign execution.
- **Sandbox-Aware Open Tracking** — Apply heuristics to identify automated scanners and sandbox activity that may distort open-rate metrics.
- **Tracked Payload Delivery** — Support controlled delivery workflows involving HTA, VBS, JS, PS1, LNK, and ISO artifacts in authorized test environments.
- **Phishing-Report Endpoint** — Provide a `/r/<token>` endpoint for instrumenting and evaluating phishing-reporting workflows.

## Architecture at a Glance

```text
SpectrePhish CLI
       |
       v
Campaign Configuration
       |
       +---- Email Template Generation
       |
       +---- Landing-Page Selection
       |
       +---- Infrastructure Preflight
       |       +-- SPF / DMARC
       |       +-- TLS / SMTP
       |       +-- Header Hygiene
       |
       v
Authorized Simulation
       |
       v
Tokenized Interaction Tracking
       |
       +---- Click Attribution
       +---- Open-Tracking Heuristics
       +---- Reporting Workflow
```

## Installation

### Prerequisites

- Git
- Python and pip, if required by the project's dependency configuration
- Go, if required by the framework's implementation
- A compatible shell environment

### Clone the Repository

```bash
git clone https://github.com/<your-username>/spectrephish.git
cd spectrephish
```

### Install Dependencies

If the repository contains a `requirements.txt` file:

```bash
python3 -m pip install -r requirements.txt
```

### Run the Installer

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

If the installer updates your Zsh configuration, reload it:

```bash
source ~/.zshrc
```

**Note:** Verify the actual repository URL, implementation language, dependency files, and installer behavior before publishing these commands. The installation steps above are based on the supplied project information; they have not been independently tested.

## Usage

SpectrePhish is intended to support controlled phishing simulations in environments where the operator has explicit authorization.

Refer to the project's CLI help and documentation for the supported commands, configuration options, campaign setup, and reporting workflows.

Example convention:

```bash
spectrephish --help
```

The command above is illustrative; use the executable name exposed by your installer.

## OPSEC and Measurement

SpectrePhish emphasizes the reliability of campaign preparation and measurement through:

- Email authentication and transport-security preflight checks.
- Header consistency and hygiene validation.
- Recipient-level attribution for authorized simulations.
- Heuristics to distinguish human interactions from automated scanning activity.
- Reporting workflows that help evaluate security-awareness controls.

Open-tracking results should be treated as estimates. Privacy protections, email clients, security gateways, image proxies, and automated scanners can affect observed activity. No heuristic can reliably classify every interaction.

## Project Scope

SpectrePhish is designed for authorized security assessments, internal phishing exercises, awareness testing, and controlled red-team simulations.

Its scope includes campaign configuration, email and landing-page generation, infrastructure checks, interaction measurement, and reporting workflows.

## Roadmap

Potential areas for future development include:

- [ ] Structured campaign reporting and export.
- [ ] Improved tracking-quality analytics.
- [ ] Campaign configuration validation.
- [ ] Integration with security-awareness workflows.
- [ ] Automated test coverage for core components.
- [ ] Documentation for deployment and configuration.

*Roadmap items are suggestions, not claims about existing functionality.*

## Author

**Inayat Hussain**
Red Team Operator | Offensive Security Engineer | Security Researcher

- **GitHub:** [@InayatHussain09](https://github.com/InayatHussain09)
- **LinkedIn:** [inayat-hussain09](https://www.linkedin.com/in/inayat-hussain09/)

## Disclaimer

SpectrePhish is intended for authorized phishing simulations, security-awareness exercises, and legitimate security research.

Only use this framework against systems, domains, infrastructure, and recipients for which you have explicit authorization. Do not use it for credential theft, unauthorized access, impersonation, or other malicious activity.

The author assumes no responsibility for misuse of this software. Users are responsible for complying with applicable laws, organizational policies, and engagement rules of authorization.

---

**SpectrePhish — Simulate. Measure. Improve.**

