from __future__ import annotations

from pathlib import Path

AUTOMATION_ID = "brand-typosquat-monitor"
STATE_DIRNAME = ".automation-state/brand-typosquat-monitor"
STATE_FILENAME = "previous_run_state.json"
SNAPSHOT_FILENAME = "current_snapshot.json"
REPORTS_DIRNAME = "reports"
DEFAULT_TLDS = ("com", "net", "org", "io")
DEFAULT_HIGH_RISK_TERMS = ("login", "auth", "secure", "support", "billing", "account")
DEFAULT_CANDIDATE_LIMIT = 75
DNS_TIMEOUT_SECONDS = 2
HTTP_TIMEOUT_SECONDS = 6
RDAP_TIMEOUT_SECONDS = 8
WHOIS_TIMEOUT_SECONDS = 8
MAX_REDIRECTS = 3
MAX_WORKERS = 12
MAX_PAGE_BYTES = 8192
MAX_HINT_CHARS = 180
SHORT_LABEL_LENGTH = 4
RECENT_REGISTRATION_DAYS = 180
PARKING_HINTS = (
    "for sale",
    "parked",
    "buy this domain",
    "afternic",
    "sedo",
    "dan.com",
    "spaceship.com",
    "porkbun.com",
    "buydomains",
    "parkingcrew",
)
MAIL_FORWARDING_HINTS = (
    "forward",
    "fwd1.",
    "fwd2.",
    "mail.protection.outlook.com",
    "secureserver.net",
)
SUSPICIOUS_TERMS = (
    "login",
    "log in",
    "sign in",
    "auth",
    "secure",
    "account",
    "billing",
    "support",
    "dashboard",
    "password",
)


def state_dir(workspace: Path) -> Path:
    return workspace / STATE_DIRNAME


def state_path(workspace: Path) -> Path:
    return state_dir(workspace) / STATE_FILENAME


def snapshot_path(workspace: Path) -> Path:
    return state_dir(workspace) / SNAPSHOT_FILENAME


def reports_dir(workspace: Path) -> Path:
    return state_dir(workspace) / REPORTS_DIRNAME
