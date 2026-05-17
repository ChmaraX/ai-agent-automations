from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import ssl
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from . import config


class MonitorBlockedError(RuntimeError):
    """Raised when the run configuration is not usable."""


@dataclass
class Scope:
    protected_brand: str
    base_labels: list[str]
    canonical_domains: list[str]
    canonical_tlds: list[str]
    tld_scope: list[str]
    high_risk_terms: list[str]


@dataclass
class Candidate:
    domain: str
    label: str
    tld: str
    reason: str
    distance: str
    is_exact_label: bool
    is_canonical: bool
    priority: int


@dataclass
class DnsEvidence:
    status: str = "unknown"
    a_records: list[str] = field(default_factory=list)
    aaaa_records: list[str] = field(default_factory=list)
    cname_records: list[str] = field(default_factory=list)
    mx_records: list[str] = field(default_factory=list)
    ns_records: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class RegistrationEvidence:
    source: str = ""
    registrar: str = ""
    registrant_organization: str = ""
    creation_date: str = ""
    expiry_date: str = ""
    status: list[str] = field(default_factory=list)
    nameservers: list[str] = field(default_factory=list)
    privacy_proxy: bool = False
    errors: list[str] = field(default_factory=list)


@dataclass
class HttpEvidence:
    reachable: bool = False
    scheme: str = ""
    status_code: int | None = None
    redirect_target: str = ""
    title: str = ""
    body_hint: str = ""
    keyword_hits: list[str] = field(default_factory=list)
    parking_detected: bool = False
    errors: list[str] = field(default_factory=list)


@dataclass
class CandidateResult:
    candidate: Candidate
    dns: DnsEvidence
    registration: RegistrationEvidence
    http: HttpEvidence
    classification: str
    confidence: str
    evidence_summary: str
    why_it_matters: str
    score: int
    review_worthy: bool
    near_miss_reason: str
    is_new_since_last_run: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": asdict(self.candidate),
            "dns": asdict(self.dns),
            "registration": asdict(self.registration),
            "http": asdict(self.http),
            "classification": self.classification,
            "confidence": self.confidence,
            "evidence_summary": self.evidence_summary,
            "why_it_matters": self.why_it_matters,
            "score": self.score,
            "review_worthy": self.review_worthy,
            "near_miss_reason": self.near_miss_reason,
            "is_new_since_last_run": self.is_new_since_last_run,
        }


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=False) + "\n")


def split_csv_like(raw: str) -> list[str]:
    items = []
    for part in re.split(r"[,\n]", raw):
        stripped = part.strip()
        if stripped:
            items.append(stripped)
    return items


def extract_domain(value: str) -> str:
    text = value.strip()
    if "://" in text:
        parsed = urlparse(text)
        host = parsed.netloc
    else:
        host = text.split("/")[0]
    host = host.split("@")[-1].strip().lower().rstrip(".")
    host = host.split(":")[0]
    return host


def registrable_domain(host: str) -> str:
    labels = [label for label in host.lower().split(".") if label]
    if len(labels) < 2:
        return host.lower()
    if len(labels) >= 3 and labels[-1] == "uk" and labels[-2] == "co":
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def keyboard_neighbors() -> dict[str, tuple[str, ...]]:
    rows = ["1234567890", "qwertyuiop", "asdfghjkl", "zxcvbnm"]
    neighbors: dict[str, set[str]] = {}
    for row in rows:
        for index, char in enumerate(row):
            bucket = neighbors.setdefault(char, set())
            if index > 0:
                bucket.add(row[index - 1])
            if index + 1 < len(row):
                bucket.add(row[index + 1])
    return {key: tuple(sorted(values)) for key, values in neighbors.items()}


KEYBOARD_NEIGHBORS = keyboard_neighbors()


def generate_variants(label: str, short_label_mode: bool) -> list[tuple[str, str, str, int]]:
    variants: dict[str, tuple[str, str, int]] = {}
    length = len(label)
    for index in range(length):
        omitted = label[:index] + label[index + 1 :]
        if len(omitted) >= 2:
            variants.setdefault(omitted, ("omitted character", "close typo", 80))
        repeated = label[: index + 1] + label[index] + label[index + 1 :]
        variants.setdefault(repeated, ("repeated character", "close typo", 78))
        if index + 1 < length:
            transposed = label[:index] + label[index + 1] + label[index] + label[index + 2 :]
            variants.setdefault(transposed, ("transposed characters", "close typo", 77))
        if not short_label_mode:
            for neighbor in KEYBOARD_NEIGHBORS.get(label[index], ()):
                substituted = label[:index] + neighbor + label[index + 1 :]
                if substituted != label:
                    variants.setdefault(substituted, ("keyboard-adjacent substitution", "close typo", 72))
    if length >= 4:
        for index in range(1, length):
            hyphenated = label[:index] + "-" + label[index:]
            variants.setdefault(hyphenated, ("hyphen insertion", "impersonation style", 70))
    return [(variant, reason, distance, priority) for variant, (reason, distance, priority) in variants.items()]


def strip_html_to_text(raw_html: str) -> str:
    raw_html = re.sub(r"(?is)<script.*?>.*?</script>", " ", raw_html)
    raw_html = re.sub(r"(?is)<style.*?>.*?</style>", " ", raw_html)
    raw_html = re.sub(r"(?s)<[^>]+>", " ", raw_html)
    raw_html = unescape(raw_html)
    return re.sub(r"\s+", " ", raw_html).strip()


class BrandTyposquatMonitorPipeline:
    def __init__(
        self,
        workspace: Path,
        brand: str,
        canonical_inputs: str,
        high_risk_terms: str,
        candidate_limit: int,
    ) -> None:
        self.workspace = workspace
        self.brand = brand.strip()
        self.canonical_inputs = canonical_inputs.strip()
        self.high_risk_terms_raw = high_risk_terms.strip()
        self.candidate_limit = candidate_limit
        self.state_dir = config.state_dir(workspace)
        self.reports_dir = config.reports_dir(workspace)
        self.state_path = config.state_path(workspace)
        self.snapshot_path = config.snapshot_path(workspace)
        self.run_timestamp = datetime.now(UTC).replace(microsecond=0)
        self.run_timestamp_str = self.run_timestamp.isoformat().replace("+00:00", "Z")
        self.prior_state = self._load_prior_state()
        self.coverage_gaps: list[str] = []
        self.runtime_notes: list[str] = []
        self.status = "ready"

    def _load_prior_state(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def run(self) -> tuple[str, dict[str, Any]]:
        if shutil.which("dig") is None:
            raise MonitorBlockedError("`dig` is not available in the runtime, so DNS evidence cannot be gathered reliably.")

        scope = self.resolve_scope()
        candidates = self.build_candidates(scope)
        results = self.collect_evidence(scope, candidates)
        findings, near_misses = self.rank_results(results)
        payload = self.build_payload(scope, candidates, findings, near_misses, results)
        markdown = self.render_markdown(payload)
        self.persist(payload, markdown)
        return markdown, payload

    def resolve_scope(self) -> Scope:
        if not self.brand or "REQUIRED_REPLACE_ME" in self.brand:
            raise MonitorBlockedError("The run configuration is incomplete: protected brand is missing.")
        if not self.canonical_inputs or "REQUIRED_REPLACE_ME" in self.canonical_inputs:
            raise MonitorBlockedError("The run configuration is incomplete: canonical domains are missing.")

        canonical_hosts = [extract_domain(value) for value in split_csv_like(self.canonical_inputs)]
        canonical_domains = []
        for host in canonical_hosts:
            registrable = registrable_domain(host)
            if "." not in registrable:
                continue
            canonical_domains.append(registrable)
        canonical_domains = sorted(dict.fromkeys(canonical_domains))
        if not canonical_domains:
            raise MonitorBlockedError("No clear canonical domain family could be extracted from the run configuration.")

        brand_labels = []
        for part in split_csv_like(self.brand):
            extracted = extract_domain(part)
            if "." in extracted:
                extracted = registrable_domain(extracted).split(".", 1)[0]
            brand_labels.append(normalize_label(extracted))
        base_labels = [label for label in brand_labels if label]
        if not base_labels:
            base_labels = [normalize_label(canonical_domains[0].split(".")[0])]
        if not base_labels or any(not label for label in base_labels):
            raise MonitorBlockedError("The protected brand could not be normalized into a usable base label.")
        unique_base_labels = sorted(dict.fromkeys(base_labels))
        if len(unique_base_labels) > 2:
            raise MonitorBlockedError("The run configuration mixes multiple unrelated brands or labels.")

        canonical_labels = sorted(dict.fromkeys(domain.split(".")[0] for domain in canonical_domains))
        if any(label not in canonical_labels and label not in unique_base_labels for label in unique_base_labels):
            # Short friendly names such as "Novu" should still match the canonical labels after normalization.
            overlap = {label for label in unique_base_labels if label in canonical_labels}
            if not overlap:
                raise MonitorBlockedError("The protected brand does not clearly map to the canonical domain family.")
            unique_base_labels = sorted(overlap)

        canonical_tlds = sorted(dict.fromkeys(domain.split(".")[-1] for domain in canonical_domains))
        tld_scope = sorted(dict.fromkeys(list(canonical_tlds) + list(config.DEFAULT_TLDS)))
        high_risk_terms = [normalize_label(term) for term in split_csv_like(self.high_risk_terms_raw)]
        if not high_risk_terms:
            high_risk_terms = list(config.DEFAULT_HIGH_RISK_TERMS)
        high_risk_terms = [term for term in high_risk_terms if term]
        return Scope(
            protected_brand=self.brand,
            base_labels=unique_base_labels,
            canonical_domains=canonical_domains,
            canonical_tlds=canonical_tlds,
            tld_scope=tld_scope,
            high_risk_terms=high_risk_terms[:6],
        )

    def build_candidates(self, scope: Scope) -> list[Candidate]:
        candidates: dict[str, Candidate] = {}
        canonical_set = set(scope.canonical_domains)

        for domain in scope.canonical_domains:
            label, tld = domain.rsplit(".", 1)
            for scoped_tld in scope.tld_scope:
                if scoped_tld == tld:
                    continue
                candidate_domain = f"{label}.{scoped_tld}"
                candidates.setdefault(
                    candidate_domain,
                    Candidate(
                        domain=candidate_domain,
                        label=label,
                        tld=scoped_tld,
                        reason="exact label on alternate TLD",
                        distance="exact label",
                        is_exact_label=True,
                        is_canonical=False,
                        priority=95,
                    ),
                )

        for label in scope.base_labels:
            short_label_mode = len(label) <= config.SHORT_LABEL_LENGTH
            for variant, reason, distance, priority in generate_variants(label, short_label_mode=short_label_mode):
                for tld in sorted(set(scope.canonical_tlds + ["com"])):
                    candidate_domain = f"{variant}.{tld}"
                    if candidate_domain in canonical_set:
                        continue
                    existing = candidates.get(candidate_domain)
                    candidate = Candidate(
                        domain=candidate_domain,
                        label=variant,
                        tld=tld,
                        reason=reason,
                        distance=distance,
                        is_exact_label=False,
                        is_canonical=False,
                        priority=priority + (4 if tld in scope.canonical_tlds else 0),
                    )
                    if existing is None or candidate.priority > existing.priority:
                        candidates[candidate_domain] = candidate

            for term in scope.high_risk_terms[:4]:
                for formatted, reason in (
                    (f"{label}-{term}", "brand plus high-risk term"),
                    (f"{term}-{label}", "high-risk term plus brand"),
                ):
                    candidate_domain = f"{formatted}.com"
                    if candidate_domain in canonical_set:
                        continue
                    candidates.setdefault(
                        candidate_domain,
                        Candidate(
                            domain=candidate_domain,
                            label=formatted,
                            tld="com",
                            reason=reason,
                            distance="high-risk combination",
                            is_exact_label=False,
                            is_canonical=False,
                            priority=62,
                        ),
                    )

        ordered = sorted(candidates.values(), key=lambda item: (-item.priority, item.domain))
        if len(ordered) > self.candidate_limit:
            ordered = ordered[: self.candidate_limit]
        return ordered

    def collect_evidence(self, scope: Scope, candidates: list[Candidate]) -> list[CandidateResult]:
        prior_domains = {
            item["candidate"]["domain"]
            for item in (self.prior_state or {}).get("results", [])
            if isinstance(item, dict) and isinstance(item.get("candidate"), dict) and item["candidate"].get("domain")
        }

        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            dns_futures = {executor.submit(self.collect_dns, candidate): candidate for candidate in candidates}
            dns_map: dict[str, DnsEvidence] = {}
            for future in as_completed(dns_futures):
                candidate = dns_futures[future]
                dns_map[candidate.domain] = future.result()

        registration_targets = [
            candidate
            for candidate in candidates
            if self.should_collect_registration(candidate, dns_map[candidate.domain])
        ]
        with ThreadPoolExecutor(max_workers=min(config.MAX_WORKERS, 8)) as executor:
            reg_futures = {executor.submit(self.collect_registration, candidate.domain): candidate for candidate in registration_targets}
            reg_map: dict[str, RegistrationEvidence] = {}
            for future in as_completed(reg_futures):
                candidate = reg_futures[future]
                reg_map[candidate.domain] = future.result()

        http_targets = [
            candidate
            for candidate in candidates
            if self.should_collect_http(candidate, dns_map[candidate.domain], reg_map.get(candidate.domain))
        ]
        with ThreadPoolExecutor(max_workers=min(config.MAX_WORKERS, 8)) as executor:
            http_futures = {executor.submit(self.collect_http, candidate.domain): candidate for candidate in http_targets}
            http_map: dict[str, HttpEvidence] = {}
            for future in as_completed(http_futures):
                candidate = http_futures[future]
                http_map[candidate.domain] = future.result()

        results = []
        for candidate in candidates:
            dns = dns_map.get(candidate.domain, DnsEvidence())
            registration = reg_map.get(candidate.domain, RegistrationEvidence())
            http = http_map.get(candidate.domain, HttpEvidence())
            classification, confidence, evidence_summary, why_it_matters, score, review_worthy, near_miss_reason = self.classify_candidate(
                scope, candidate, dns, registration, http
            )
            if dns.errors or registration.errors or http.errors:
                self.status = "partial"
            result = CandidateResult(
                candidate=candidate,
                dns=dns,
                registration=registration,
                http=http,
                classification=classification,
                confidence=confidence,
                evidence_summary=evidence_summary,
                why_it_matters=why_it_matters,
                score=score,
                review_worthy=review_worthy,
                near_miss_reason=near_miss_reason,
                is_new_since_last_run=candidate.domain not in prior_domains,
            )
            results.append(result)
        return results

    def should_collect_registration(self, candidate: Candidate, dns: DnsEvidence) -> bool:
        if candidate.is_exact_label:
            return True
        if dns.status not in {"NXDOMAIN", "unknown"}:
            return True
        if dns.ns_records or dns.mx_records or dns.a_records or dns.aaaa_records or dns.cname_records:
            return True
        return False

    def should_collect_http(
        self,
        candidate: Candidate,
        dns: DnsEvidence,
        registration: RegistrationEvidence | None,
    ) -> bool:
        if dns.a_records or dns.aaaa_records or dns.cname_records:
            return True
        if candidate.is_exact_label and registration and registration.creation_date:
            return True
        return False

    def collect_dns(self, candidate: Candidate) -> DnsEvidence:
        evidence = DnsEvidence()
        a_result = self.run_dig(candidate.domain, "A", include_status=True)
        evidence.status = a_result["status"] or "unknown"
        evidence.a_records = a_result["records"]
        if not evidence.a_records:
            evidence.aaaa_records = self.run_dig(candidate.domain, "AAAA")["records"]
        if not evidence.a_records and not evidence.aaaa_records:
            evidence.cname_records = self.run_dig(candidate.domain, "CNAME")["records"]
        if evidence.status != "NXDOMAIN" or candidate.is_exact_label:
            evidence.mx_records = self.run_dig(candidate.domain, "MX")["records"]
            evidence.ns_records = self.run_dig(candidate.domain, "NS")["records"]
        errors = []
        for result in (a_result,):
            errors.extend(result["errors"])
        evidence.errors = sorted(dict.fromkeys(errors))
        return evidence

    def run_dig(self, domain: str, record_type: str, include_status: bool = False) -> dict[str, Any]:
        result = {"status": "", "records": [], "errors": []}
        args = ["dig", f"+time={config.DNS_TIMEOUT_SECONDS}", "+tries=1", domain, record_type, "+short"]
        try:
            completed = subprocess.run(args, capture_output=True, text=True, timeout=config.DNS_TIMEOUT_SECONDS + 1)
            result["records"] = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
            if completed.stderr.strip():
                result["errors"].append(completed.stderr.strip())
        except subprocess.TimeoutExpired:
            result["errors"].append(f"{record_type} lookup timed out")
            return result
        if include_status:
            try:
                comments = subprocess.run(
                    ["dig", f"+time={config.DNS_TIMEOUT_SECONDS}", "+tries=1", domain, record_type, "+noall", "+comments"],
                    capture_output=True,
                    text=True,
                    timeout=config.DNS_TIMEOUT_SECONDS + 1,
                )
                match = re.search(r"status:\s*([A-Z]+)", comments.stdout)
                if match:
                    result["status"] = match.group(1)
                if comments.stderr.strip():
                    result["errors"].append(comments.stderr.strip())
            except subprocess.TimeoutExpired:
                result["errors"].append(f"{record_type} status lookup timed out")
        return result

    def collect_registration(self, domain: str) -> RegistrationEvidence:
        rdap = self.fetch_rdap(domain)
        if rdap.source:
            return rdap
        if shutil.which("whois") is not None:
            whois = self.fetch_whois(domain)
            if whois.source:
                return whois
            merged_errors = rdap.errors + whois.errors
            rdap.errors = sorted(dict.fromkeys(merged_errors))
        else:
            rdap.errors.append("whois not available")
        return rdap

    def fetch_rdap(self, domain: str) -> RegistrationEvidence:
        evidence = RegistrationEvidence(source="rdap")
        url = f"https://rdap.org/domain/{domain}"
        request = Request(url, headers={"Accept": "application/rdap+json", "User-Agent": f"{config.AUTOMATION_ID}/1.0"})
        try:
            with urlopen(request, timeout=config.RDAP_TIMEOUT_SECONDS, context=ssl.create_default_context()) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except Exception as exc:
            evidence.source = ""
            evidence.errors.append(f"RDAP lookup failed: {exc}")
            return evidence

        evidence.registrar = self.extract_registrar_from_rdap(payload)
        evidence.registrant_organization, evidence.privacy_proxy = self.extract_registrant_from_rdap(payload)
        evidence.creation_date = self.extract_event_date(payload, "registration")
        evidence.expiry_date = self.extract_event_date(payload, "expiration")
        evidence.status = list(payload.get("status", []))
        evidence.nameservers = [ns.get("ldhName", "") for ns in payload.get("nameservers", []) if ns.get("ldhName")]
        return evidence

    def extract_registrar_from_rdap(self, payload: dict[str, Any]) -> str:
        for entity in payload.get("entities", []):
            roles = entity.get("roles", [])
            if "registrar" not in roles:
                continue
            vcard = entity.get("vcardArray")
            if isinstance(vcard, list) and len(vcard) > 1:
                for row in vcard[1]:
                    if row[0] == "fn":
                        return str(row[3])
        return ""

    def extract_registrant_from_rdap(self, payload: dict[str, Any]) -> tuple[str, bool]:
        org_name = ""
        privacy_proxy = False
        for entity in payload.get("entities", []):
            roles = set(entity.get("roles", []))
            if not roles.intersection({"registrant", "administrative"}):
                continue
            vcard = entity.get("vcardArray")
            if not (isinstance(vcard, list) and len(vcard) > 1):
                continue
            for row in vcard[1]:
                if row[0] in {"fn", "org"}:
                    value = str(row[3])
                    if value:
                        org_name = value
                        lowered = value.lower()
                        if "privacy" in lowered or "proxy" in lowered or "redacted" in lowered:
                            privacy_proxy = True
        return org_name, privacy_proxy

    def extract_event_date(self, payload: dict[str, Any], event_action: str) -> str:
        for event in payload.get("events", []):
            if event.get("eventAction") == event_action:
                return str(event.get("eventDate", ""))
        return ""

    def fetch_whois(self, domain: str) -> RegistrationEvidence:
        evidence = RegistrationEvidence(source="whois")
        try:
            completed = subprocess.run(
                ["whois", domain],
                capture_output=True,
                text=True,
                timeout=config.WHOIS_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            evidence.source = ""
            evidence.errors.append("WHOIS lookup timed out")
            return evidence
        raw = completed.stdout
        if not raw.strip():
            evidence.source = ""
            stderr = completed.stderr.strip()
            evidence.errors.append(stderr or "WHOIS lookup returned no data")
            return evidence

        evidence.registrar = self.first_match(raw, r"(?im)^Registrar:\s*(.+)$")
        evidence.registrant_organization = self.first_match(raw, r"(?im)^Registrant Organization:\s*(.+)$")
        evidence.creation_date = self.first_match(raw, r"(?im)^(?:Creation Date|Created On):\s*(.+)$")
        evidence.expiry_date = self.first_match(raw, r"(?im)^(?:Registry Expiry Date|Expiry Date|Expiration Date):\s*(.+)$")
        evidence.status = re.findall(r"(?im)^Domain Status:\s*(.+)$", raw)
        evidence.nameservers = re.findall(r"(?im)^Name Server:\s*(.+)$", raw)
        lowered = evidence.registrant_organization.lower()
        evidence.privacy_proxy = any(token in lowered for token in ("privacy", "proxy", "redacted")) if lowered else False
        return evidence

    def first_match(self, text: str, pattern: str) -> str:
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    def collect_http(self, domain: str) -> HttpEvidence:
        evidence = HttpEvidence()
        for scheme in ("https", "http"):
            url = f"{scheme}://{domain}"
            try:
                request = Request(
                    url,
                    headers={
                        "User-Agent": f"{config.AUTOMATION_ID}/1.0",
                        "Accept": "text/html,application/xhtml+xml",
                    },
                )
                with urlopen(request, timeout=config.HTTP_TIMEOUT_SECONDS, context=ssl._create_unverified_context()) as response:
                    body = response.read(config.MAX_PAGE_BYTES).decode("utf-8", errors="replace")
                    final_url = response.geturl()
                    evidence.reachable = True
                    evidence.scheme = scheme
                    evidence.status_code = response.getcode()
                    if final_url.rstrip("/") != url.rstrip("/"):
                        evidence.redirect_target = final_url
                    evidence.title = self.extract_title(body)
                    text_hint = strip_html_to_text(body)
                    evidence.body_hint = text_hint[: config.MAX_HINT_CHARS]
                    lowered = f"{evidence.title} {evidence.body_hint}".lower()
                    evidence.keyword_hits = [term for term in config.SUSPICIOUS_TERMS if term in lowered]
                    evidence.parking_detected = any(term in lowered for term in config.PARKING_HINTS)
                    return evidence
            except Exception as exc:
                evidence.errors.append(f"{scheme.upper()} failed: {exc}")
        return evidence

    def extract_title(self, body: str) -> str:
        match = re.search(r"<title[^>]*>(.*?)</title>", body, flags=re.I | re.S)
        if not match:
            return ""
        return re.sub(r"\s+", " ", unescape(match.group(1))).strip()

    def classify_candidate(
        self,
        scope: Scope,
        candidate: Candidate,
        dns: DnsEvidence,
        registration: RegistrationEvidence,
        http: HttpEvidence,
    ) -> tuple[str, str, str, str, int, bool, str]:
        signals: list[str] = []
        score = 0
        recently_registered = self.is_recent_registration(registration.creation_date)
        has_mail = self.has_live_mx(dns.mx_records)
        mail_forwarding = any(hint in " ".join(dns.mx_records).lower() for hint in config.MAIL_FORWARDING_HINTS)
        active_web = http.reachable and http.status_code is not None and http.status_code < 500
        brand_mentioned = self.brand_mentioned(scope, http)
        suspicious_web_copy = len(http.keyword_hits) >= 2 or (brand_mentioned and bool(http.keyword_hits))
        parked = http.parking_detected or any(term in http.redirect_target.lower() for term in config.PARKING_HINTS)
        unrelated_brand = self.looks_unrelated_brand(candidate, scope, http)
        exact_label = candidate.is_exact_label
        close_same_tld = candidate.tld in scope.canonical_tlds and candidate.distance != "exact label"
        nx_or_dead = dns.status == "NXDOMAIN" and not any([dns.a_records, dns.aaaa_records, dns.cname_records, dns.mx_records, dns.ns_records])

        if exact_label:
            score += 18
            signals.append("exact label on alternate TLD")
        if close_same_tld:
            score += 22
            signals.append("close typo on canonical TLD")
        if has_mail:
            score += 10
            signals.append("active MX records")
        if mail_forwarding:
            score += 14
            signals.append("mail-forwarding MX pattern")
        if active_web:
            score += 10
            signals.append("active HTTP/HTTPS response")
        if suspicious_web_copy:
            score += 18
            signals.append("login/account/support wording")
        if http.redirect_target:
            score += 8
            signals.append(f"redirects to {http.redirect_target}")
        if recently_registered:
            score += 8
            signals.append("recent registration")
        if registration.privacy_proxy:
            score += 4
            signals.append("privacy/proxy registration")
        if parked:
            score -= 18
            signals.append("parking or resale behavior")
        if unrelated_brand:
            score -= 30
            signals.append("page appears to belong to another brand")
        if nx_or_dead:
            score -= 30

        review_worthy = score >= 32 and not nx_or_dead
        if suspicious_web_copy and (active_web or has_mail) and not parked and not unrelated_brand:
            classification = "high-risk"
            confidence = "Medium"
        elif review_worthy:
            classification = "watchlist"
            confidence = "Medium-High" if mail_forwarding or suspicious_web_copy or exact_label else "Medium"
        elif active_web or has_mail or exact_label:
            classification = "likely benign"
            confidence = "Medium"
        else:
            classification = "no evidence"
            confidence = "Low"

        if unrelated_brand and not mail_forwarding and not (close_same_tld and recently_registered):
            classification = "likely benign" if (active_web or has_mail or exact_label) else "no evidence"
            confidence = "Medium"
        if parked and not mail_forwarding and not (close_same_tld and recently_registered):
            classification = "likely benign"
            confidence = "Medium"
        if (
            classification == "watchlist"
            and close_same_tld
            and not has_mail
            and not mail_forwarding
            and not suspicious_web_copy
            and not recently_registered
            and not http.redirect_target
            and not exact_label
        ):
            classification = "likely benign"
            confidence = "Medium"
        if classification == "high-risk" and (parked or unrelated_brand):
            classification = "watchlist"
            confidence = "Medium"

        evidence_summary = self.build_evidence_summary(dns, registration, http, candidate, recently_registered)
        why_it_matters = self.build_why_it_matters(candidate, classification, mail_forwarding, suspicious_web_copy, exact_label, close_same_tld, parked)
        near_miss_reason = ""
        if classification != "watchlist" and classification != "high-risk":
            near_miss_reason = self.build_near_miss_reason(classification, parked, unrelated_brand, candidate, dns, http)
        return classification, confidence, evidence_summary, why_it_matters, score, review_worthy, near_miss_reason

    def is_recent_registration(self, creation_date: str) -> bool:
        if not creation_date:
            return False
        cleaned = creation_date.replace("Z", "+00:00")
        try:
            created = datetime.fromisoformat(cleaned)
        except ValueError:
            return False
        return (self.run_timestamp - created.astimezone(UTC)).days <= config.RECENT_REGISTRATION_DAYS

    def has_live_mx(self, mx_records: list[str]) -> bool:
        for record in mx_records:
            normalized = record.strip().lower()
            if normalized in {"0 .", "0 localhost."}:
                continue
            if normalized.endswith(" .") or normalized.endswith(" localhost."):
                continue
            if normalized:
                return True
        return False

    def brand_mentioned(self, scope: Scope, http: HttpEvidence) -> bool:
        haystack = " ".join([http.title.lower(), http.body_hint.lower(), http.redirect_target.lower()])
        return any(label in haystack for label in scope.base_labels if label)

    def looks_unrelated_brand(self, candidate: Candidate, scope: Scope, http: HttpEvidence) -> bool:
        if not http.title and not http.body_hint and not http.redirect_target:
            return False
        brand_terms = set(scope.base_labels)
        target_text = " ".join([http.title.lower(), http.body_hint.lower(), http.redirect_target.lower()])
        for term in brand_terms:
            if term and term in target_text:
                return False
        # Obvious parking pages are handled elsewhere.
        if any(hint in target_text for hint in config.PARKING_HINTS):
            return False
        # For short labels, a different apparent brand is common; only mark unrelated when title exists.
        return bool(http.title)

    def build_evidence_summary(
        self,
        dns: DnsEvidence,
        registration: RegistrationEvidence,
        http: HttpEvidence,
        candidate: Candidate,
        recently_registered: bool,
    ) -> str:
        parts = []
        if dns.status and dns.status != "unknown":
            parts.append(f"DNS status `{dns.status}`")
        if dns.a_records:
            parts.append(f"A `{'; '.join(dns.a_records[:2])}`")
        elif dns.cname_records:
            parts.append(f"CNAME `{'; '.join(dns.cname_records[:2])}`")
        if dns.mx_records:
            parts.append(f"MX `{'; '.join(dns.mx_records[:2])}`")
        if registration.creation_date:
            created = registration.creation_date.split("T", 1)[0]
            parts.append(f"{registration.source.upper()} creation `{created}`")
        if registration.registrar:
            parts.append(f"registrar `{registration.registrar}`")
        if http.reachable and http.status_code is not None:
            parts.append(f"{http.scheme.upper()} `{http.status_code}`")
        if http.redirect_target:
            parts.append(f"redirect `{http.redirect_target}`")
        if http.title:
            parts.append(f"title `{http.title[:80]}`")
        if http.keyword_hits:
            parts.append(f"keyword hits `{', '.join(http.keyword_hits[:4])}`")
        if recently_registered:
            parts.append("recent registration")
        if candidate.is_exact_label:
            parts.append("exact-label alternate TLD")
        return "; ".join(parts) if parts else "No public DNS, registration, or HTTP evidence was observed."

    def build_why_it_matters(
        self,
        candidate: Candidate,
        classification: str,
        mail_forwarding: bool,
        suspicious_web_copy: bool,
        exact_label: bool,
        close_same_tld: bool,
        parked: bool,
    ) -> str:
        if classification in {"high-risk", "watchlist"}:
            reasons = []
            if close_same_tld:
                reasons.append("same-TLD typo near the canonical domain")
            if exact_label:
                reasons.append("exact label likely to catch cross-TLD mistakes")
            if mail_forwarding:
                reasons.append("mail capability increases phishing or misdelivery risk")
            if suspicious_web_copy:
                reasons.append("page wording overlaps with account or support flows")
            if parked and not reasons:
                reasons.append("close variant exists and could change behavior later")
            return "; ".join(reasons) if reasons else "Close brand variant with some public activity worth human review."
        if parked:
            return "Currently behaves like a parked or resale domain rather than an active impersonation site."
        if exact_label:
            return "Exact-label alternate TLD exists, but current evidence did not show impersonation behavior."
        return "Observed evidence was weak, unrelated, or inactive."

    def build_near_miss_reason(
        self,
        classification: str,
        parked: bool,
        unrelated_brand: bool,
        candidate: Candidate,
        dns: DnsEvidence,
        http: HttpEvidence,
    ) -> str:
        if classification == "no evidence":
            return f"`{candidate.domain}` had no meaningful DNS or web activity in this run."
        if parked:
            return f"`{candidate.domain}` resolved, but the observed page behavior matched parking or resale."
        if unrelated_brand:
            return f"`{candidate.domain}` was active, but the visible branding appeared unrelated to the protected brand."
        if dns.mx_records and not http.reachable:
            return f"`{candidate.domain}` published MX but did not show stronger web evidence."
        if http.reachable:
            return f"`{candidate.domain}` was active, but observed evidence did not justify escalation."
        return f"`{candidate.domain}` did not clear the review threshold."

    def rank_results(self, results: list[CandidateResult]) -> tuple[list[CandidateResult], list[CandidateResult]]:
        ranked = sorted(results, key=lambda item: (-item.score, item.candidate.domain))
        findings = [item for item in ranked if item.classification in {"high-risk", "watchlist"}][:10]
        near_misses = [item for item in ranked if item not in findings and item.near_miss_reason][:10]
        if not findings and near_misses:
            near_misses = near_misses[:8]
        return findings, near_misses

    def build_payload(
        self,
        scope: Scope,
        candidates: list[Candidate],
        findings: list[CandidateResult],
        near_misses: list[CandidateResult],
        results: list[CandidateResult],
    ) -> dict[str, Any]:
        canonical_display = ", ".join(scope.canonical_domains)
        coverage = self.build_coverage_summary(results)
        if not findings:
            summary = "No candidate in this bounded run cleared the threshold for `high-risk`. The strongest review items, if any, stayed at `watchlist` or below."
        else:
            summary = f"{len(findings)} candidate(s) looked worth human review in this bounded run. None should be treated as comprehensive coverage beyond the configured brand family and TLD scope."
        if self.prior_state is None:
            self.runtime_notes.append("No prior state was available, so this run is snapshot-only.")
        else:
            self.runtime_notes.append("A prior state file was available for simple new-domain comparison.")

        coverage_gaps = sorted(dict.fromkeys(self.coverage_gaps))
        if not coverage_gaps and self.status == "partial":
            coverage_gaps.append("Some DNS, RDAP, WHOIS, or HTTP checks timed out or returned incomplete data.")
        if not coverage_gaps:
            coverage_gaps.append("No major collection gaps were recorded beyond the normal limits of a bounded public-data scan.")

        manual_follow_up = []
        for item in findings[:2]:
            if item.classification in {"high-risk", "watchlist"}:
                manual_follow_up.append(
                    f"Recheck `{item.candidate.domain}` for content or DNS changes, especially MX, redirects, and account-like wording."
                )
        if not manual_follow_up:
            manual_follow_up.append("No immediate follow-up is warranted beyond the next scheduled run.")

        payload = {
            "run_time_utc": self.run_timestamp_str,
            "protected_brand": scope.protected_brand,
            "canonical_domains": scope.canonical_domains,
            "resolved_tld_scope": scope.tld_scope,
            "candidate_count": len(candidates),
            "coverage": coverage,
            "status": self.status,
            "summary": summary,
            "ranked_findings": [item.to_dict() for item in findings],
            "near_misses": [item.to_dict() for item in near_misses],
            "coverage_gaps": coverage_gaps,
            "suggested_manual_follow_up": manual_follow_up[:2],
            "runtime_notes": self.runtime_notes,
            "results": [item.to_dict() for item in results],
        }
        return payload

    def build_coverage_summary(self, results: list[CandidateResult]) -> str:
        dns_count = len(results)
        rdap_count = sum(1 for item in results if item.registration.source == "rdap")
        whois_count = sum(1 for item in results if item.registration.source == "whois")
        http_count = sum(1 for item in results if item.http.reachable or item.http.errors)
        if any(item.registration.errors for item in results):
            self.coverage_gaps.append("Some RDAP or WHOIS lookups failed or timed out; registration evidence may be incomplete.")
        if any(item.http.errors for item in results):
            self.coverage_gaps.append("Some HTTP or HTTPS checks failed or timed out; page-title evidence may be incomplete.")
        return f"DNS checked for {dns_count} candidates; registration checked for {rdap_count + whois_count}; HTTP/HTTPS checked for {http_count}."

    def render_markdown(self, payload: dict[str, Any]) -> str:
        lines = [
            "# Brand Typosquat Monitor",
            f"Run time: {payload['run_time_utc']}",
            f"Protected brand: `{payload['protected_brand']}`",
            f"Canonical domains: `{', '.join(payload['canonical_domains'])}`",
            f"Resolved TLD scope: `{', '.join(payload['resolved_tld_scope'])}`",
            f"Candidate count: `{payload['candidate_count']}`",
            f"Coverage: {payload['coverage']}",
            f"Status: `{payload['status']}`",
            "",
            "## Summary",
            payload["summary"],
            "",
            "## Ranked Findings",
            "| Domain | Classification | Evidence | Why It Matters | Confidence |",
            "|---|---|---|---|---|",
        ]
        if payload["ranked_findings"]:
            for item in payload["ranked_findings"]:
                lines.append(
                    f"| `{item['candidate']['domain']}` | `{item['classification']}` | {self.escape_table(item['evidence_summary'])} | {self.escape_table(item['why_it_matters'])} | {item['confidence']} |"
                )
        else:
            lines.append("| None | `no suspicious result` | No candidate cleared the bounded review threshold. | Strongest near-misses are listed below. | Low |")

        lines.extend(["", "## Near Misses And Parked Domains"])
        if payload["near_misses"]:
            for item in payload["near_misses"]:
                lines.append(f"- {item['near_miss_reason']}")
        else:
            lines.append("- No additional near-misses were retained in this bounded run.")

        lines.extend(["", "## Coverage Gaps"])
        for gap in payload["coverage_gaps"]:
            lines.append(f"- {gap}")

        lines.extend(["", "## Suggested Manual Follow-Up"])
        for follow_up in payload["suggested_manual_follow_up"]:
            lines.append(f"- {follow_up}")
        lines.append("")
        return "\n".join(lines)

    def escape_table(self, text: str) -> str:
        return text.replace("|", "\\|")

    def persist(self, payload: dict[str, Any], markdown: str) -> None:
        timestamp = self.run_timestamp.strftime("%Y%m%dT%H%M%SZ")
        json_path = self.reports_dir / f"{timestamp}.json"
        md_path = self.reports_dir / f"{timestamp}.md"
        atomic_write_json(json_path, payload)
        atomic_write_text(md_path, markdown)
        atomic_write_json(self.snapshot_path, payload)
        atomic_write_json(self.state_path, payload)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the brand typosquat monitor pipeline.")
    parser.add_argument("--workspace", default=".", help="Workspace root where state and reports should be written.")
    parser.add_argument("--brand", required=True, help="Protected brand or company name.")
    parser.add_argument("--canonical", required=True, help="Comma-separated canonical domains or URLs.")
    parser.add_argument(
        "--high-risk-terms",
        default=",".join(config.DEFAULT_HIGH_RISK_TERMS),
        help="Comma-separated high-risk terms to optionally combine with the brand.",
    )
    parser.add_argument(
        "--candidate-limit",
        type=int,
        default=config.DEFAULT_CANDIDATE_LIMIT,
        help="Maximum number of generated candidate domains to inspect.",
    )
    return parser.parse_args(argv)
