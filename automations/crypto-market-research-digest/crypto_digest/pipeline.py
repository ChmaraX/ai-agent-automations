from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from html import unescape
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from . import config, fetchers, renderers

OFAC_NAMESPACE = {"ofac": "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/XML"}
TERM_PATTERNS = [
    ("bitcoin", re.compile(r"\bbitcoin\b", re.I)),
    ("btc", re.compile(r"\bbtc\b", re.I)),
    ("ether", re.compile(r"\bether\b", re.I)),
    ("eth", re.compile(r"\beth\b", re.I)),
    ("ethereum", re.compile(r"\bethereum\b", re.I)),
    ("crypto", re.compile(r"\bcrypto\b", re.I)),
    ("crypto asset", re.compile(r"\bcrypto assets?\b", re.I)),
    ("digital asset", re.compile(r"\bdigital assets?\b", re.I)),
    ("blockchain", re.compile(r"\bblockchain\b", re.I)),
    ("token", re.compile(r"\btokens?\b", re.I)),
    ("stablecoin", re.compile(r"\bstablecoins?\b", re.I)),
    ("staking", re.compile(r"\bstaking\b", re.I)),
    ("custody", re.compile(r"\bcustod(?:y|ial)\b", re.I)),
    ("wallet", re.compile(r"\bwallets?\b", re.I)),
    ("mining", re.compile(r"\bmining\b", re.I)),
    ("tokenization", re.compile(r"\btokenization\b", re.I)),
    ("defi", re.compile(r"\bde[- ]?fi\b", re.I)),
    ("ofac", re.compile(r"\bofac\b", re.I)),
    ("sanctions", re.compile(r"\bsanctions?\b", re.I)),
    ("ransomware", re.compile(r"\bransomware\b", re.I)),
]
HIGH_SIGNAL_TERMS = {
    "bitcoin",
    "btc",
    "ether",
    "eth",
    "ethereum",
    "crypto",
    "crypto asset",
    "digital asset",
    "stablecoin",
    "staking",
    "custody",
    "wallet",
    "mining",
    "tokenization",
    "defi",
    "ofac",
    "sanctions",
    "ransomware",
}
WHY_IT_MATTERS = {
    "Financial exposure": "Quarterly disclosure references bitcoin or digital-asset exposure that can change reported sensitivity to crypto prices.",
    "Custody/staking-related": "Custody or staking language can affect fee mix, client balances, and related regulatory exposure.",
    "Tokenization-related": "Stablecoin or tokenization language can affect payments-product positioning and regulatory oversight.",
    "Mining-related": "Mining language can change production, power-cost, or fleet expansion expectations.",
    "Operational update": "Current-report language indicates operating developments linked to crypto products or activity.",
    "Legal/regulatory issue": "Sanctions or compliance language can alter counterparty screening and regulatory risk.",
    "Repeated boilerplate": "The filing looks similar to prior crypto-related disclosure and may be context rather than a new signal.",
    "Risk factor": "The filing contains crypto-related risk language that still warrants review even if it may be repeated.",
    "ETF/product filing": "Product-registration language can change listed-vehicle or issuance exposure to crypto markets.",
    "Requires review": "Crypto terms appear in the filing body, but the context needs manual review before drawing conclusions.",
}


@dataclass
class StatusRow:
    source: str
    status: str
    records_checked: int
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "status": self.status,
            "records_checked": self.records_checked,
            "notes": self.notes,
        }


def safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def compute_percent_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous in (None, 0):
        return None
    return (current - previous) / previous * 100.0


def strip_html_to_text(raw_html: str) -> str:
    raw_html = re.sub(r"(?is)<script.*?>.*?</script>", " ", raw_html)
    raw_html = re.sub(r"(?is)<style.*?>.*?</style>", " ", raw_html)
    raw_html = re.sub(r"(?is)<ix:header.*?>.*?</ix:header>", " ", raw_html)
    raw_html = re.sub(r"(?s)<[^>]+>", " ", raw_html)
    raw_html = unescape(raw_html)
    return re.sub(r"\s+", " ", raw_html).strip()


def build_term_windows(text: str, terms: list[str], window_radius: int = 180) -> list[str]:
    windows: list[str] = []
    lowered = text.lower()
    for term in terms:
        pattern = re.compile(rf".{{0,{window_radius}}}{re.escape(term.lower())}.{{0,{window_radius}}}")
        windows.extend(pattern.findall(lowered))
        if len(windows) >= 6:
            break
    return windows


def classify_sec_item(ticker: str, form: str, matches: list[str], windows: list[str]) -> tuple[str, str]:
    match_set = set(matches)
    joined_windows = " ".join(windows)
    if ticker == "PYPL" and match_set & {"stablecoin", "tokenization", "crypto", "digital asset"}:
        return "Tokenization-related", "High"
    if ticker == "COIN" and match_set & {"stablecoin", "tokenization", "staking", "custody"}:
        return "Tokenization-related", "High"
    if ticker == "MSTR" and match_set & {"bitcoin", "btc", "crypto", "digital asset"}:
        return "Financial exposure", "High"
    if ticker == "XYZ" and match_set & {"bitcoin", "btc", "crypto", "digital asset"}:
        return "Financial exposure", "High"
    if ticker in config.MINER_TICKERS and (match_set & {"mining", "bitcoin", "btc", "crypto", "digital asset"}):
        return "Mining-related", "High"
    if match_set & {"stablecoin", "tokenization"}:
        return "Tokenization-related", "High"
    if match_set & {"staking", "custody", "wallet"}:
        return "Custody/staking-related", "High"
    if "risk factors" in joined_windows and not (match_set & {"stablecoin", "staking", "custody", "mining"}):
        return "Risk factor", "Medium"
    if match_set & {"ofac", "sanctions", "ransomware"}:
        return "Legal/regulatory issue", "Medium"
    if "business" in joined_windows or "operations" in joined_windows:
        return "Operational update", "Medium"
    if form in {"S-1", "S-3", "F-1", "N-1A", "N-2", "NPORT-P"} or any(
        form.startswith(prefix) for prefix in config.SEC_PRIORITY_FORM_PREFIXES
    ):
        return "ETF/product filing", "Medium"
    return "Requires review", "Medium"


def make_source_key(source_name: str) -> str:
    return source_name.lower().replace(" ", "_")


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


class DigestPipeline:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.run_date = datetime.now(timezone.utc).date()
        self.run_date_str = self.run_date.isoformat()
        self.run_timestamp_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        self.lookback_start = self.run_date - timedelta(days=6)
        self.status_rows: list[StatusRow] = []
        self.failures: list[str] = []
        self.state_dir = config.state_dir(workspace)
        self.reports_dir = config.reports_dir(workspace)
        self.cache_dir = config.cache_dir(workspace)
        self.state_path = config.state_path(workspace)
        self.snapshot_path = config.snapshot_path(workspace)
        self.prior_state, self.mode, self.state_note = self._load_prior_state()
        self.prior_markets = (self.prior_state or {}).get("markets", {})
        self.prior_sec_index = {
            (item.get("ticker"), item.get("filing"), item.get("date"), item.get("accession_number")): item
            for item in (self.prior_state or {}).get("sec_relevant_items", [])
        }
        self.prior_ofac_index = {
            (
                item.get("name"),
                item.get("program"),
                item.get("address_type"),
                item.get("address_value"),
                item.get("source"),
            )
            for item in (self.prior_state or {}).get("ofac_crypto_relevant_items", [])
        }
        self.prior_run_date = (self.prior_state or {}).get("run_date_utc")

    def _load_prior_state(self) -> tuple[dict[str, Any] | None, str, str]:
        if not self.state_path.exists():
            return None, "snapshot-only", "Snapshot-only run because no prior normalized state was available."
        try:
            payload = json.loads(self.state_path.read_text())
        except Exception as exc:
            return None, "snapshot-only", f"Snapshot-only run because the prior normalized state was unreadable ({exc})."
        prior_date = payload.get("run_date_utc", "unknown date")
        if prior_date == self.run_date_str:
            note = f"Diff-aware run using an earlier normalized snapshot from {prior_date}."
        else:
            note = f"Diff-aware run using prior normalized state from {prior_date}."
        return payload, "diff-aware", note

    def add_status(self, source: str, status: str, records_checked: int, notes: str) -> None:
        self.status_rows.append(StatusRow(source, status, records_checked, notes))
        if status == "Failed":
            self.failures.append(f"{source}: {notes}")

    def fetch_all(self) -> dict[str, Any]:
        fetched: dict[str, Any] = {}

        try:
            fetched["binance"] = fetchers.fetch_binance_pairs(config.DEFAULT_PAIRS)
            self.add_status(
                "Binance 24h tickers",
                "OK",
                len(fetched["binance"]),
                f"Tracked {len(fetched['binance'])} of {len(config.DEFAULT_PAIRS)} requested pairs.",
            )
        except Exception as exc:
            fetched["binance"] = []
            self.add_status("Binance 24h tickers", "Failed", 0, str(exc))

        binance_candles: dict[str, list[list[Any]]] = {}
        candle_ok = 0
        for symbol in config.BINANCE_CANDLE_FEATURED_PAIRS:
            try:
                rows = fetchers.fetch_binance_klines(
                    symbol,
                    interval=config.BINANCE_CANDLE_INTERVAL,
                    limit=config.BINANCE_CANDLE_LIMIT,
                )
                if isinstance(rows, list) and rows:
                    binance_candles[symbol] = rows
                    candle_ok += 1
            except Exception:
                continue
        fetched["binance_candles"] = binance_candles
        self.add_status(
            "Binance featured klines",
            "OK" if candle_ok == len(config.BINANCE_CANDLE_FEATURED_PAIRS) else ("Partial" if candle_ok else "Failed"),
            candle_ok,
            f"Fetched {candle_ok} of {len(config.BINANCE_CANDLE_FEATURED_PAIRS)} featured {config.BINANCE_CANDLE_INTERVAL} candle sets.",
        )

        source_specs = [
            ("DeFiLlama protocols", "protocols", fetchers.fetch_json, config.DEFILLAMA_PROTOCOLS),
            ("DeFiLlama chains", "chains", fetchers.fetch_json, config.DEFILLAMA_CHAINS),
            ("Stablecoins", "stablecoins", fetchers.fetch_json, config.DEFILLAMA_STABLECOINS),
            ("DeFiLlama fees", "fees", fetchers.fetch_json, config.DEFILLAMA_FEES),
            ("DeFiLlama dexs", "dexs", fetchers.fetch_json, config.DEFILLAMA_DEXS),
            ("DeFiLlama yields", "yields", fetchers.fetch_json, config.DEFILLAMA_YIELDS),
        ]
        for source_name, key, loader, url in source_specs:
            try:
                payload = loader(url, timeout=75)
                fetched[key] = payload
                count = len(payload) if isinstance(payload, list) else len(payload.get("data", payload.get("protocols", payload.get("peggedAssets", []))))
                note = {
                    "protocols": "Protocol TVL universe loaded.",
                    "chains": "Requested endpoint exposes current TVL only.",
                    "stablecoins": "Includes chain-level current, prior-day, and prior-week supply fields.",
                    "fees": "Revenue field not cleanly exposed in this overview endpoint.",
                    "dexs": "DEX volume leaders loaded.",
                    "yields": "Yield pool universe loaded.",
                }[key]
                self.add_status(source_name, "OK", count, note)
            except Exception as exc:
                fetched[key] = [] if key in {"protocols", "chains"} else {}
                self.add_status(source_name, "Failed", 0, str(exc))

        try:
            sec_ticker_map, used_cache = fetchers.fetch_sec_ticker_map(self.cache_dir)
            fetched["sec_ticker_map"] = sec_ticker_map
            note = "Ticker-to-CIK map loaded with SEC User-Agent header."
            if used_cache:
                note += " Cached copy reused."
            self.add_status("SEC company tickers", "OK", len(sec_ticker_map), note)
        except Exception as exc:
            fetched["sec_ticker_map"] = {}
            self.add_status("SEC company tickers", "Failed", 0, str(exc))

        sec_submissions: dict[str, dict[str, Any]] = {}
        checked = 0
        ticker_lookup = {
            value["ticker"].upper(): str(value["cik_str"]).zfill(10)
            for value in fetched["sec_ticker_map"].values()
        }
        for ticker in config.DEFAULT_WATCHLIST:
            cik = ticker_lookup.get(ticker) or config.SEC_CIK_OVERRIDES.get(ticker)
            if cik and len(cik) != 10 and cik.isdigit():
                cik = cik.zfill(10)
            if not cik:
                continue
            try:
                sec_submissions[ticker] = fetchers.fetch_sec_submission(cik)
                checked += 1
            except Exception:
                continue
        fetched["sec_submissions"] = sec_submissions
        self.add_status(
            "SEC submissions",
            "OK" if checked else "Partial",
            checked,
            f"Checked {checked} watchlist submission feeds for {self.lookback_start.isoformat()} to {self.run_date_str}.",
        )

        try:
            fetched["ofac_sdn"] = fetchers.fetch_ofac_tree(config.OFAC_SDN_XML)
            sdn_count = self._count_ofac_digital_currency_rows(fetched["ofac_sdn"])
            self.add_status("OFAC SDN XML", "OK", sdn_count, "Parsed exact-listed digital currency address entries from official XML.")
        except Exception as exc:
            fetched["ofac_sdn"] = None
            self.add_status("OFAC SDN XML", "Failed", 0, str(exc))

        try:
            fetched["ofac_consolidated"] = fetchers.fetch_ofac_tree(config.OFAC_CONSOLIDATED_XML)
            extra_count = self._count_ofac_digital_currency_rows(fetched["ofac_consolidated"])
            note = "Parsed exact-listed digital currency address entries from official XML."
            if extra_count == 0:
                note = "No additional digital-currency address rows were exposed beyond the SDN-style entry set."
            self.add_status("OFAC consolidated XML", "OK", extra_count, note)
        except Exception as exc:
            fetched["ofac_consolidated"] = None
            self.add_status("OFAC consolidated XML", "Failed", 0, str(exc))

        return fetched

    def _count_ofac_digital_currency_rows(self, root: ElementTree.Element | None) -> int:
        if root is None:
            return 0
        count = 0
        for entry in root.findall(".//ofac:sdnEntry", OFAC_NAMESPACE):
            for identifier in entry.findall(".//ofac:id", OFAC_NAMESPACE):
                identifier_type = identifier.findtext("ofac:idType", default="", namespaces=OFAC_NAMESPACE)
                identifier_value = identifier.findtext("ofac:idNumber", default="", namespaces=OFAC_NAMESPACE)
                if "Digital Currency Address" in identifier_type and identifier_value:
                    count += 1
        return count

    def normalize(self, fetched: dict[str, Any]) -> dict[str, Any]:
        markets = self._normalize_markets(fetched.get("binance", []))
        featured_candles = self._normalize_featured_candles(fetched.get("binance_candles", {}))
        defi = self._normalize_defi(fetched)
        sec_items = self._normalize_sec(fetched)
        ofac_items = self._normalize_ofac(fetched)

        normalized_state = {
            "automation_id": config.AUTOMATION_ID,
            "run_date_utc": self.run_date_str,
            "run_timestamp_utc": self.run_timestamp_utc,
            "mode": self.mode,
            "compared_to_run_date_utc": self.prior_run_date,
            "compared_to_run_timestamp_utc": (self.prior_state or {}).get("run_timestamp_utc"),
            "sources": {make_source_key(row.source): row.to_dict() for row in self.status_rows},
            "markets": markets,
            "featured_candles": featured_candles,
            "defi": defi,
            "sec_relevant_items": sec_items,
            "ofac_crypto_relevant_items": ofac_items,
            "notes": [
                self.state_note,
                f"SEC lookback window: {self.lookback_start.isoformat()} to {self.run_date_str}.",
                f"OFAC exact-listed crypto-relevant records: {len(ofac_items)}.",
            ],
        }
        self.validate(normalized_state)
        return normalized_state

    def _normalize_markets(self, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        markets: dict[str, dict[str, Any]] = {}
        for row in rows:
            symbol = row.get("symbol")
            if symbol not in config.DEFAULT_PAIRS:
                continue
            markets[symbol] = {
                "last_price": safe_float(row.get("lastPrice")),
                "price_change_percent_24h": safe_float(row.get("priceChangePercent")),
                "high_24h": safe_float(row.get("highPrice")),
                "low_24h": safe_float(row.get("lowPrice")),
                "quote_volume_24h": safe_float(row.get("quoteVolume")),
                "close_time_ms": row.get("closeTime"),
            }
        return markets

    def _normalize_featured_candles(self, rows_by_symbol: dict[str, list[list[Any]]]) -> dict[str, list[dict[str, Any]]]:
        normalized: dict[str, list[dict[str, Any]]] = {}
        for symbol, rows in rows_by_symbol.items():
            candles: list[dict[str, Any]] = []
            for row in rows:
                if not isinstance(row, list) or len(row) < 7:
                    continue
                candles.append(
                    {
                        "open_time_ms": row[0],
                        "open": safe_float(row[1]),
                        "high": safe_float(row[2]),
                        "low": safe_float(row[3]),
                        "close": safe_float(row[4]),
                        "volume": safe_float(row[5]),
                        "close_time_ms": row[6],
                    }
                )
            if candles:
                normalized[symbol] = candles
        return normalized

    def _normalize_defi(self, fetched: dict[str, Any]) -> dict[str, Any]:
        chain_rows = [
            {"name": row.get("name"), "tvl": safe_float(row.get("tvl"))}
            for row in fetched.get("chains", [])
            if safe_float(row.get("tvl")) is not None
        ]
        chain_rows.sort(key=lambda item: item["tvl"], reverse=True)

        protocols = []
        for row in fetched.get("protocols", []):
            tvl = safe_float(row.get("tvl"))
            if tvl is None or tvl <= 0 or row.get("category") == "CEX":
                continue
            protocols.append(
                {
                    "name": row.get("name"),
                    "category": row.get("category") or "N/A",
                    "chain": row.get("chain") or ", ".join((row.get("chains") or [])[:2]) or "N/A",
                    "tvl": tvl,
                    "change_1d": safe_float(row.get("change_1d")),
                    "change_7d": safe_float(row.get("change_7d")),
                }
            )
        protocols.sort(key=lambda item: item["tvl"], reverse=True)

        fees = []
        for row in fetched.get("fees", {}).get("protocols", []):
            total_24h = safe_float(row.get("total24h"))
            if total_24h is None:
                continue
            fees.append(
                {
                    "protocol": row.get("displayName") or row.get("name") or "Unknown",
                    "fees": total_24h,
                    "revenue": None,
                    "change_1d": safe_float(row.get("change_1d")),
                }
            )
        fees.sort(key=lambda item: item["fees"], reverse=True)

        dexs = []
        for row in fetched.get("dexs", {}).get("protocols", []):
            total_24h = safe_float(row.get("total24h"))
            if total_24h is None:
                continue
            dexs.append(
                {
                    "protocol": row.get("displayName") or row.get("name") or "Unknown",
                    "volume": total_24h,
                    "change_1d": safe_float(row.get("change_1d")),
                }
            )
        dexs.sort(key=lambda item: item["volume"], reverse=True)

        stablecoin_assets = []
        stablecoin_chains: dict[str, dict[str, float]] = {}
        for asset in fetched.get("stablecoins", {}).get("peggedAssets", []):
            current = safe_float((asset.get("circulating") or {}).get("peggedUSD"))
            prev_day = safe_float((asset.get("circulatingPrevDay") or {}).get("peggedUSD"))
            prev_week = safe_float((asset.get("circulatingPrevWeek") or {}).get("peggedUSD"))
            if current is not None:
                stablecoin_assets.append(
                    {
                        "name": asset.get("symbol") or asset.get("name"),
                        "supply": current,
                        "prev_day": prev_day,
                        "prev_week": prev_week,
                    }
                )
            for chain_name, values in (asset.get("chainCirculating") or {}).items():
                bucket = stablecoin_chains.setdefault(chain_name, {"current": 0.0, "prev_day": 0.0, "prev_week": 0.0})
                current_chain = safe_float(((values.get("current") or {}).get("peggedUSD")))
                prev_day_chain = safe_float(((values.get("circulatingPrevDay") or {}).get("peggedUSD")))
                prev_week_chain = safe_float(((values.get("circulatingPrevWeek") or {}).get("peggedUSD")))
                if current_chain is not None:
                    bucket["current"] += current_chain
                if prev_day_chain is not None:
                    bucket["prev_day"] += prev_day_chain
                if prev_week_chain is not None:
                    bucket["prev_week"] += prev_week_chain
        stablecoin_assets.sort(key=lambda item: item["supply"], reverse=True)
        stablecoin_chain_rows = [
            {"chain": name, **values}
            for name, values in stablecoin_chains.items()
        ]
        stablecoin_chain_rows.sort(key=lambda item: item["current"], reverse=True)

        yield_outliers = []
        seen_pools: set[tuple[str, str, str]] = set()
        for row in fetched.get("yields", {}).get("data", []):
            apy = safe_float(row.get("apy"))
            tvl = safe_float(row.get("tvlUsd"))
            project = (row.get("project") or "").lower()
            if apy is None or tvl is None or apy <= config.YIELD_APY_THRESHOLD:
                continue
            if tvl < config.YIELD_SECONDARY_TVL_THRESHOLD:
                continue
            if tvl < config.YIELD_PRIMARY_TVL_THRESHOLD and not (
                apy >= 80 or project in config.KNOWN_PROTOCOLS
            ):
                continue
            pool_key = (row.get("project") or "", row.get("chain") or "", row.get("symbol") or "")
            if pool_key in seen_pools:
                continue
            seen_pools.add(pool_key)
            quality_penalty = 0
            reason = "APY above 25% with meaningful TVL."
            if apy >= config.YIELD_EXTREME_APY_THRESHOLD:
                quality_penalty += 2
                reason = "Extreme APY may reflect incentive distortion or low-utilization mechanics; review closely."
            elif apy >= 200:
                quality_penalty += 1
                reason = "Very high APY likely depends on incentives or transient conditions."
            if tvl < config.YIELD_PRIMARY_TVL_THRESHOLD:
                quality_penalty += 1
                reason += " Included below the primary $5M TVL threshold because the protocol or APY still warrants review."
            if row.get("ilRisk") not in (None, "no", "unknown"):
                reason += f" Reported IL risk: {row.get('ilRisk')}."
            yield_outliers.append(
                {
                    "pool": row.get("poolMeta") or row.get("symbol") or row.get("pool") or "Unknown",
                    "protocol": row.get("project") or "Unknown",
                    "chain": row.get("chain") or "Unknown",
                    "apy": apy,
                    "tvl": tvl,
                    "ilRisk": row.get("ilRisk") or "unknown",
                    "reason": reason,
                    "quality_penalty": quality_penalty,
                    "known_protocol": project in config.KNOWN_PROTOCOLS,
                }
            )
        yield_outliers.sort(
            key=lambda item: (
                item["quality_penalty"],
                0 if item["known_protocol"] else 1,
                0 if item["tvl"] >= config.YIELD_PRIMARY_TVL_THRESHOLD else 1,
                -min(item["apy"], 5000.0),
                -item["tvl"],
            )
        )

        return {
            "chains": chain_rows[:25],
            "protocols": protocols[:50],
            "fees": fees[:25],
            "dexs": dexs[:25],
            "stablecoins": stablecoin_assets[:25],
            "stablecoin_chains": stablecoin_chain_rows[:25],
            "yield_outliers": yield_outliers[: config.TOP_YIELD_COUNT],
        }

    def _normalize_sec(self, fetched: dict[str, Any]) -> list[dict[str, Any]]:
        ticker_map = {
            value["ticker"].upper(): str(value["cik_str"]).zfill(10)
            for value in fetched.get("sec_ticker_map", {}).values()
        }
        candidates: list[dict[str, Any]] = []
        for ticker, submission in fetched.get("sec_submissions", {}).items():
            cik = ticker_map.get(ticker) or config.SEC_CIK_OVERRIDES.get(ticker)
            if cik and len(cik) != 10 and cik.isdigit():
                cik = cik.zfill(10)
            recent = (submission.get("filings") or {}).get("recent") or {}
            for form, filing_date, accession_number, primary_document in zip(
                recent.get("form", []),
                recent.get("filingDate", []),
                recent.get("accessionNumber", []),
                recent.get("primaryDocument", []),
            ):
                try:
                    filing_day = date.fromisoformat(filing_date)
                except ValueError:
                    continue
                if not (self.lookback_start <= filing_day <= self.run_date):
                    continue
                if form not in config.SEC_PRIORITY_FORMS and not any(
                    form.startswith(prefix) for prefix in config.SEC_PRIORITY_FORM_PREFIXES
                ):
                    continue
                candidates.append(
                    {
                        "ticker": ticker,
                        "company": submission.get("name") or ticker,
                        "cik": cik,
                        "filing": form,
                        "date": filing_date,
                        "accession_number": accession_number,
                        "primary_document": primary_document,
                    }
                )

        items: list[dict[str, Any]] = []
        best_by_ticker: dict[str, dict[str, Any]] = {}
        for candidate in sorted(candidates, key=lambda row: (row["date"], row["ticker"], row["filing"]), reverse=True):
            if candidate["primary_document"].lower().endswith((".xml", ".pdf", ".txt")):
                continue
            try:
                filing_html = fetchers.fetch_sec_filing_text(
                    candidate["cik"],
                    candidate["accession_number"],
                    candidate["primary_document"],
                )
            except Exception:
                continue
            filing_text = strip_html_to_text(filing_html)
            matches = [label for label, pattern in TERM_PATTERNS if pattern.search(filing_text)]
            if not matches or not (set(matches) & HIGH_SIGNAL_TERMS):
                continue
            windows = build_term_windows(filing_text, matches)
            topic, confidence = classify_sec_item(candidate["ticker"], candidate["filing"], matches, windows)
            prior_key = (
                candidate["ticker"],
                candidate["filing"],
                candidate["date"],
                candidate["accession_number"],
            )
            if prior_key in self.prior_sec_index:
                topic = "Repeated boilerplate"
                confidence = "Low"
            item = {
                "company": candidate["company"],
                "ticker": candidate["ticker"],
                "filing": candidate["filing"],
                "date": candidate["date"],
                "topic": topic,
                "why_it_matters": WHY_IT_MATTERS[topic],
                "priority": "High" if confidence == "High" else "Medium",
                "confidence": confidence,
                "accession_number": candidate["accession_number"],
                "matched_terms": sorted(set(matches)),
                "classification": topic,
            }
            current_best = best_by_ticker.get(candidate["ticker"])
            if current_best is None or self._sec_sort_key(item) < self._sec_sort_key(current_best):
                best_by_ticker[candidate["ticker"]] = item
        items = sorted(best_by_ticker.values(), key=self._sec_sort_key)
        return items[:8]

    def _sec_sort_key(self, item: dict[str, Any]) -> tuple[int, str, str]:
        priority_rank = 0 if item["priority"] == "High" else 1
        return (priority_rank, item["date"], item["ticker"])

    def _normalize_ofac(self, fetched: dict[str, Any]) -> list[dict[str, Any]]:
        all_items: dict[tuple[str, str, str, str], dict[str, Any]] = {}
        for source_name, root in (
            ("OFAC SDN XML", fetched.get("ofac_sdn")),
            ("OFAC consolidated XML", fetched.get("ofac_consolidated")),
        ):
            if root is None:
                continue
            for entry in root.findall(".//ofac:sdnEntry", OFAC_NAMESPACE):
                name = " ".join(
                    part
                    for part in [
                        entry.findtext("ofac:firstName", default="", namespaces=OFAC_NAMESPACE),
                        entry.findtext("ofac:lastName", default="", namespaces=OFAC_NAMESPACE),
                    ]
                    if part
                ).strip() or entry.findtext("ofac:lastName", default="", namespaces=OFAC_NAMESPACE)
                programs = ", ".join(
                    program.text
                    for program in entry.findall(".//ofac:program", OFAC_NAMESPACE)
                    if program.text
                ) or "N/A"
                for identifier in entry.findall(".//ofac:id", OFAC_NAMESPACE):
                    identifier_type = identifier.findtext("ofac:idType", default="", namespaces=OFAC_NAMESPACE)
                    identifier_value = identifier.findtext("ofac:idNumber", default="", namespaces=OFAC_NAMESPACE)
                    if "Digital Currency Address" not in identifier_type or not identifier_value:
                        continue
                    dedupe_key = (name, programs, identifier_type, identifier_value)
                    item = {
                        "name": name,
                        "program": programs,
                        "address_type": identifier_type,
                        "address_value": identifier_value,
                        "source": source_name,
                    }
                    all_items.setdefault(dedupe_key, item)
        return list(all_items.values())

    def validate(self, normalized_state: dict[str, Any]) -> None:
        compared_to = normalized_state.get("compared_to_run_date_utc")
        if normalized_state["mode"] == "diff-aware" and not compared_to:
            raise RuntimeError("Diff-aware mode requires a prior run date baseline.")
        if (
            compared_to == normalized_state["run_date_utc"]
            and normalized_state.get("compared_to_run_timestamp_utc") == normalized_state["run_timestamp_utc"]
        ):
            raise RuntimeError("Invalid state baseline: current run timestamp matches the loaded comparison baseline.")
        if any(
            item["source"] == "OFAC SDN XML" and item["records_checked"] == 0 and item["status"] == "OK"
            for item in normalized_state["sources"].values()
        ):
            raise RuntimeError("OFAC SDN XML cannot be marked OK with zero parsed rows.")

    def build_report(self, normalized_state: dict[str, Any]) -> dict[str, Any]:
        markets = normalized_state["markets"]
        market_entries = [
            {"pair": symbol, **payload}
            for symbol, payload in markets.items()
        ]
        market_entries.sort(key=lambda row: row["price_change_percent_24h"] or -999.0, reverse=True)
        breadth_positive = sum(1 for row in market_entries if (row["price_change_percent_24h"] or 0) > 0)
        breadth_negative = sum(1 for row in market_entries if (row["price_change_percent_24h"] or 0) < 0)
        leader = market_entries[0] if market_entries else None
        laggard = min(market_entries, key=lambda row: row["price_change_percent_24h"] or 999.0) if market_entries else None
        volume_leader = max(market_entries, key=lambda row: row["quote_volume_24h"] or -1.0) if market_entries else None
        close_timestamp = None
        if market_entries:
            close_timestamp = max(row["close_time_ms"] for row in market_entries if row.get("close_time_ms"))
        market_rows = []
        for symbol in config.DEFAULT_PAIRS:
            row = markets.get(symbol)
            if row is None:
                continue
            note_parts: list[str] = []
            if leader and symbol == leader["pair"]:
                note_parts.append("Top 24h gainer in tracked set.")
            if laggard and symbol == laggard["pair"]:
                if (laggard["price_change_percent_24h"] or 0) < 0:
                    note_parts.append("Top 24h decliner in tracked set.")
                else:
                    note_parts.append("Lowest 24h return in tracked set.")
            if volume_leader and symbol == volume_leader["pair"]:
                note_parts.append("Highest quote volume in tracked set.")
            previous_market = self.prior_markets.get(symbol)
            if previous_market:
                delta = compute_percent_change(row["last_price"], previous_market.get("last_price"))
                baseline_label = f"earlier {self.prior_run_date} snapshot" if self.prior_run_date == self.run_date_str else self.prior_run_date
                note_parts.append(f"Vs {baseline_label}: {renderers.format_percent(delta)} price change.")
            elif self.prior_state:
                note_parts.append("No prior normalized pair state for cross-run comparison.")
            market_rows.append(
                {
                    "asset": symbol.replace("USDT", ""),
                    "pair": symbol,
                    "last_price": renderers.format_price(row["last_price"]),
                    "change_24h": renderers.format_percent(row["price_change_percent_24h"], 3),
                    "change_value_24h": row["price_change_percent_24h"] or 0.0,
                    "quote_volume_24h": renderers.format_money(row["quote_volume_24h"]),
                    "note": " ".join(note_parts) or "Tracked Binance 24h snapshot.",
                }
            )

        chain_rows = normalized_state["defi"]["chains"][: config.TOP_CHAIN_COUNT]
        protocol_rows = self._select_protocol_rows(normalized_state["defi"]["protocols"])
        fee_rows = normalized_state["defi"]["fees"][: config.TOP_FEES_COUNT]
        dex_rows = normalized_state["defi"]["dexs"][: config.TOP_DEX_COUNT]
        stable_rows, stable_summary, significant_chain_mover = self._build_stablecoin_section(
            normalized_state["defi"]["stablecoins"],
            normalized_state["defi"]["stablecoin_chains"],
        )
        yield_rows = self._build_yield_rows(normalized_state["defi"]["yield_outliers"])
        sec_rows = self._build_sec_rows(normalized_state["sec_relevant_items"])
        sanctions_rows = self._build_ofac_rows(normalized_state["ofac_crypto_relevant_items"])
        insight_sections = self._build_insight_sections(
            leader=leader,
            laggard=laggard,
            volume_leader=volume_leader,
            breadth_positive=breadth_positive,
            breadth_negative=breadth_negative,
            chain_rows=chain_rows,
            protocol_rows=protocol_rows,
            fee_rows=fee_rows,
            dex_rows=dex_rows,
            stable_rows=stable_rows,
            significant_chain_mover=significant_chain_mover,
            yield_rows=yield_rows,
            sec_rows=sec_rows,
            sanctions_rows=sanctions_rows,
        )
        executive_summary = self._build_executive_summary(
            leader=leader,
            laggard=laggard,
            volume_leader=volume_leader,
            chain_rows=chain_rows,
            protocol_rows=protocol_rows,
            stable_rows=stable_rows,
            yield_rows=yield_rows,
            sec_rows=sec_rows,
            sanctions_rows=sanctions_rows,
            ofac_row_count=len(normalized_state["ofac_crypto_relevant_items"]),
        )

        if close_timestamp:
            close_utc = datetime.fromtimestamp(close_timestamp / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            market_narrative = [
                f"The tracked Binance snapshot closed at {close_utc} on the exchange feed. Breadth across the nine tracked pairs was {breadth_positive} positive and {breadth_negative} negative on a 24-hour basis, which is exchange-level activity rather than a full market-wide view.",
                f"Leadership was concentrated in {leader['pair'].replace('USDT', '') if leader else 'N/A'} on the upside and {laggard['pair'].replace('USDT', '') if laggard else 'N/A'} on the downside, while {volume_leader['pair'].replace('USDT', '') if volume_leader else 'N/A'} carried the deepest quote volume. Cross-run price deltas versus {('an earlier ' + self.prior_run_date + ' snapshot') if self.prior_run_date == self.run_date_str else (self.prior_run_date or 'the next persistent baseline')} are only available where the prior normalized state actually stored the pair.",
            ]
        else:
            market_narrative = ["Market data fetch failed, so no cautious interpretation is possible for this section."]

        limitations = self._build_limitations()
        report = {
            "run_date_utc": self.run_date_str,
            "mode": self.mode,
            "executive_summary": executive_summary,
            "analyst_readout": insight_sections,
            "source_fetch_status": [row.to_dict() for row in self.status_rows],
            "market_pulse": {"rows": market_rows, "narrative": market_narrative},
            "defi_fundamentals": {
                "chains": [
                    {
                        "chain": row["name"],
                        "tvl": renderers.format_money(row["tvl"]),
                        "change_1d": "N/A",
                        "change_7d": "N/A",
                        "note": "Requested endpoint exposes current TVL only.",
                    }
                    for row in chain_rows
                ],
                "protocols": protocol_rows,
                "fees": [
                    {
                        "protocol": row["protocol"],
                        "fees": renderers.format_money(row["fees"]),
                        "revenue": "N/A",
                        "change": renderers.format_percent(row["change_1d"]),
                        "note": (
                            "1d move exceeded the 20% flag threshold; revenue remains source-limited."
                            if row["change_1d"] is not None and abs(row["change_1d"]) > config.FEE_DEX_MOVE_THRESHOLD
                            else "Revenue source-limited in this endpoint."
                        ),
                    }
                    for row in fee_rows
                ],
                "dexs": [
                    {
                        "protocol": row["protocol"],
                        "volume": renderers.format_money(row["volume"]),
                        "change": renderers.format_percent(row["change_1d"]),
                        "note": (
                            "1d move exceeded the 20% flag threshold."
                            if row["change_1d"] is not None and abs(row["change_1d"]) > config.FEE_DEX_MOVE_THRESHOLD
                            else "Top 24h DEX volume leader."
                        ),
                    }
                    for row in dex_rows
                ],
            },
            "stablecoin_monitor": {
                "rows": stable_rows,
                "summary": stable_summary,
            },
            "yield_outliers": yield_rows,
            "sec_filing_monitor": {
                "rows": sec_rows,
                "empty_note": "" if sec_rows else "> No material crypto-related SEC filing changes were found in the checked sources.",
            },
            "sanctions_monitor": {"rows": sanctions_rows},
            "research_watchlist": self._build_watchlist(leader, protocol_rows, significant_chain_mover, yield_rows, sec_rows, sanctions_rows),
            "limitations": limitations,
            "summary_cards": {
                "market_leader": f"{leader['pair']} {renderers.format_percent(leader['price_change_percent_24h'], 3)}" if leader else "N/A",
                "top_chain": f"{chain_rows[0]['name']} {renderers.format_money(chain_rows[0]['tvl'])}" if chain_rows else "N/A",
                "sec_rows": len(sec_rows),
                "ofac_rows": len(normalized_state["ofac_crypto_relevant_items"]),
            },
        }
        return report

    def _select_protocol_rows(self, protocols: list[dict[str, Any]]) -> list[dict[str, str]]:
        selected: list[dict[str, Any]] = []
        seen: set[str] = set()
        for row in protocols[:3]:
            selected.append(row)
            seen.add(row["name"])
        movers = [
            row
            for row in protocols
            if row["change_1d"] is not None
            and abs(row["change_1d"]) > config.PROTOCOL_MOVE_THRESHOLD
            and row["tvl"] >= 250_000_000
            and row["name"] not in seen
        ]
        movers.sort(key=lambda item: (abs(item["change_1d"]), item["tvl"]), reverse=True)
        for row in movers[:2]:
            selected.append(row)
            seen.add(row["name"])
        for row in protocols:
            if len(selected) >= config.TOP_PROTOCOL_COUNT:
                break
            if row["name"] not in seen:
                selected.append(row)
                seen.add(row["name"])
        result = []
        for row in selected[: config.TOP_PROTOCOL_COUNT]:
            note = "Top TVL protocol."
            if row["change_1d"] is not None and abs(row["change_1d"]) > config.PROTOCOL_MOVE_THRESHOLD:
                note = "Flagged because source-exposed 1d TVL move exceeded 10%."
            result.append(
                {
                    "protocol": row["name"],
                    "category": row["category"],
                    "chain": row["chain"],
                    "tvl": renderers.format_money(row["tvl"]),
                    "change": f"1d {renderers.format_percent(row['change_1d'])} / 7d {renderers.format_percent(row['change_7d'])}",
                    "research_note": note,
                }
            )
        return result

    def _build_stablecoin_section(
        self,
        assets: list[dict[str, Any]],
        chains: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], str, dict[str, Any] | None]:
        rows: list[dict[str, Any]] = []
        significant_chain_mover: dict[str, Any] | None = None
        for asset in assets[: config.TOP_STABLECOIN_ASSET_COUNT]:
            day_change = compute_percent_change(asset["supply"], asset["prev_day"])
            week_change = compute_percent_change(asset["supply"], asset["prev_week"])
            note = "Stablecoin supply leader."
            if day_change is not None and abs(day_change) > config.STABLECOIN_CHAIN_MOVE_THRESHOLD:
                note += " 1d move exceeded the 5% flag threshold."
            rows.append(
                {
                    "label": asset["name"],
                    "supply": renderers.format_money(asset["supply"]),
                    "change": f"1d {renderers.format_percent(day_change)} / 7d {renderers.format_percent(week_change)}",
                    "change_value_day": day_change,
                    "note": note,
                }
            )
        chain_candidates: list[dict[str, Any]] = []
        for chain in chains:
            day_change = compute_percent_change(chain["current"], chain["prev_day"])
            week_change = compute_percent_change(chain["current"], chain["prev_week"])
            chain_candidates.append({**chain, "day_change": day_change, "week_change": week_change})
        for chain in chain_candidates[: config.TOP_STABLECOIN_CHAIN_COUNT]:
            note = "Chain stablecoin supply leader."
            if chain["day_change"] is not None and abs(chain["day_change"]) > config.STABLECOIN_CHAIN_MOVE_THRESHOLD:
                note += " 1d move exceeded the 5% flag threshold."
            rows.append(
                {
                    "label": chain["chain"],
                    "supply": renderers.format_money(chain["current"]),
                    "change": f"1d {renderers.format_percent(chain['day_change'])} / 7d {renderers.format_percent(chain['week_change'])}",
                    "change_value_day": chain["day_change"],
                    "note": note,
                }
            )
        significant_moves = [
            chain
            for chain in chain_candidates
            if chain["current"] >= 100_000_000
            and chain["day_change"] is not None
            and abs(chain["day_change"]) > config.STABLECOIN_CHAIN_MOVE_THRESHOLD
        ]
        significant_moves.sort(key=lambda item: abs(item["day_change"]), reverse=True)
        if significant_moves:
            significant_chain_mover = significant_moves[0]
            summary = (
                "Large chain-level stablecoin supply changes were not broad across every major chain in this slice. "
                f"The strongest 1-day move among chains with at least $100M supply was {significant_chain_mover['chain']} at "
                f"{renderers.format_percent(significant_chain_mover['day_change'])}, which looks more chain-specific than market-wide on this run."
            )
        else:
            summary = (
                "Major stablecoin supply changes looked limited in the current slice; the largest leaders were still "
                "concentrated on the biggest chains rather than showing a broad-based cross-chain surge."
            )
        return rows, summary, significant_chain_mover

    def _build_yield_rows(self, yield_outliers: list[dict[str, Any]]) -> list[dict[str, str]]:
        rows = []
        for item in yield_outliers[: config.TOP_YIELD_COUNT]:
            priority = "High" if item["apy"] >= 60 or item["tvl"] >= 50_000_000 else "Medium"
            rows.append(
                {
                    "pool_protocol": f"{item['pool']} / {item['protocol']}",
                    "chain": item["chain"],
                    "apy": renderers.format_percent(item["apy"]),
                    "tvl": renderers.format_money(item["tvl"]),
                    "reason_flagged": item["reason"],
                    "review_priority": priority,
                    "apy_value": item["apy"],
                }
            )
        return rows

    def _build_sec_rows(self, sec_items: list[dict[str, Any]]) -> list[dict[str, str]]:
        return [
            {
                "company": item["company"],
                "ticker": item["ticker"],
                "filing": item["filing"],
                "date": item["date"],
                "topic": item["topic"],
                "why_it_matters": item["why_it_matters"],
                "priority": item["priority"],
                "confidence": item["confidence"],
            }
            for item in sec_items
        ]

    def _build_ofac_rows(self, ofac_items: list[dict[str, Any]]) -> list[dict[str, str]]:
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for item in ofac_items:
            grouped.setdefault((item["name"], item["program"], item["source"]), []).append(item)
        rows = []
        for (name, program, source), entries in grouped.items():
            entries.sort(key=lambda row: row["address_value"])
            type_counts: dict[str, int] = {}
            for entry in entries:
                network = entry["address_type"].replace("Digital Currency Address - ", "")
                type_counts[network] = type_counts.get(network, 0) + 1
            sample_type = sorted(type_counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
            change_type = (
                f"Newly observed vs {self.prior_run_date} local state"
                if self.prior_state and any(
                    (entry["name"], entry["program"], entry["address_type"], entry["address_value"], entry["source"])
                    not in self.prior_ofac_index
                    for entry in entries
                )
                else "Observed in current snapshot"
            )
            rows.append(
                {
                    "item": name,
                    "source": source,
                    "change_type": change_type,
                    "crypto_relevance": f"{len(entries)} exact-listed {sample_type} address records; programs: {program}.",
                    "review_priority": "High" if any(tag in program for tag in ["CYBER", "DPRK", "RUSSIA"]) else "Medium",
                }
            )
        rows.sort(
            key=lambda row: (
                0 if row["item"].upper() in config.PREFERRED_OFAC_NAMES else 1,
                -int(re.search(r"(\d+)", row["crypto_relevance"]).group(1)) if re.search(r"(\d+)", row["crypto_relevance"]) else 0,
                row["item"],
            )
        )
        return rows[:6]

    def _build_executive_summary(
        self,
        *,
        leader: dict[str, Any] | None,
        laggard: dict[str, Any] | None,
        volume_leader: dict[str, Any] | None,
        chain_rows: list[dict[str, Any]],
        protocol_rows: list[dict[str, str]],
        stable_rows: list[dict[str, Any]],
        yield_rows: list[dict[str, str]],
        sec_rows: list[dict[str, str]],
        sanctions_rows: list[dict[str, str]],
        ofac_row_count: int,
    ) -> list[str]:
        bullets = [
            f"{self.state_note} Prior state was partial, so some cross-run comparisons remain source-limited even though this run is {self.mode}.",
        ]
        if leader and laggard and volume_leader:
            weakest_phrase = (
                f"{laggard['pair']} was the weakest at {renderers.format_percent(laggard['price_change_percent_24h'], 3)}"
                if (laggard["price_change_percent_24h"] or 0) < 0
                else f"{laggard['pair']} had the lowest positive return at {renderers.format_percent(laggard['price_change_percent_24h'], 3)}"
            )
            bullets.append(
                f"Within the tracked Binance set, {leader['pair']} led 24-hour gains at {renderers.format_percent(leader['price_change_percent_24h'], 3)}, {weakest_phrase}, and {volume_leader['pair']} had the largest quote volume at {renderers.format_money(volume_leader['quote_volume_24h'])}."
            )
        if chain_rows:
            bullets.append(
                f"DeFiLlama chain TVL remained led by {chain_rows[0]['name']} at {renderers.format_money(chain_rows[0]['tvl'])}; the requested chains endpoint did not expose 1-day or 7-day chain TVL changes."
            )
        mover_rows = [row for row in protocol_rows if "exceeded 10%" in row["research_note"]]
        if mover_rows:
            bullets.append(
                "Protocol TVL movers above the 10% flag threshold were source-exposed, including "
                + "; ".join(row["protocol"] + " " + row["change"].split(" / ")[0].replace("1d ", "") for row in mover_rows[:2])
                + "."
            )
        else:
            bullets.append("No meaningful protocol TVL move above the 10% flag threshold appeared in the selected source-exposed slice.")
        if stable_rows:
            bullets.append(
                f"Stablecoin supply remained concentrated in {stable_rows[0]['label']} at {stable_rows[0]['supply']}; chain-level supply changes above 5% were checked from DeFiLlama’s current versus prior-day fields."
            )
        if yield_rows:
            bullets.append(
                f"{len(yield_rows)} yield pools met the outlier screen of APY above 25%, with preference for TVL above $5M; these are potential risk signals, not safety assessments."
            )
        if sec_rows:
            bullets.append(
                f"SEC monitoring found {len(sec_rows)} crypto-relevant watchlist filings dated between {self.lookback_start.isoformat()} and {self.run_date_str} after filing-text review, led by fresh quarterly or current reports from {', '.join(row['ticker'] for row in sec_rows[:4])}."
            )
        else:
            bullets.append(
                f"No material crypto-related SEC filing rows were retained after checking watchlist submissions and filing text for {self.lookback_start.isoformat()} through {self.run_date_str}."
            )
        bullets.append(
            f"OFAC parsing identified {ofac_row_count} exact-listed digital-currency address rows across the official XML downloads; {len(sanctions_rows)} grouped highlights are shown below, and newly observed items require cautious interpretation because the prior OFAC state on {self.prior_run_date or 'the next persistent baseline'} was empty or source-limited."
        )
        return bullets[:8]

    def _build_insight_sections(
        self,
        *,
        leader: dict[str, Any] | None,
        laggard: dict[str, Any] | None,
        volume_leader: dict[str, Any] | None,
        breadth_positive: int,
        breadth_negative: int,
        chain_rows: list[dict[str, Any]],
        protocol_rows: list[dict[str, str]],
        fee_rows: list[dict[str, Any]],
        dex_rows: list[dict[str, Any]],
        stable_rows: list[dict[str, Any]],
        significant_chain_mover: dict[str, Any] | None,
        yield_rows: list[dict[str, str]],
        sec_rows: list[dict[str, str]],
        sanctions_rows: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        sections: list[dict[str, str]] = []

        if leader and laggard and volume_leader:
            breadth_phrase = (
                f"All {breadth_positive} tracked pairs were positive on the 24-hour Binance snapshot."
                if breadth_positive and breadth_negative == 0
                else f"Market breadth was mixed, with {breadth_positive} positive pairs and {breadth_negative} negative pairs."
            )
            sections.append(
                {
                    "title": "Market Structure",
                    "summary": (
                        f"{breadth_phrase} Leadership came from {leader['pair'].replace('USDT', '')}, while liquidity still sat with "
                        f"{volume_leader['pair'].replace('USDT', '')}. That points to broad exchange-level risk appetite, but with participation "
                        "stronger in alt leadership than in benchmark-volume leadership."
                    ),
                }
            )

        if chain_rows:
            top_protocol_names = ", ".join(row["protocol"] for row in protocol_rows[:3]) if protocol_rows else "the usual large protocols"
            hot_dex = dex_rows[0]["protocol"] if dex_rows else "top DEX venues"
            sections.append(
                {
                    "title": "DeFi Posture",
                    "summary": (
                        f"TVL stayed concentrated in established platforms, with {chain_rows[0]['name']} still the largest chain and "
                        f"{top_protocol_names} anchoring the protocol table. That suggests the capital base looks stable at the top, even while "
                        f"trading activity remained more dynamic in venues like {hot_dex}."
                    ),
                }
            )

        if stable_rows:
            if significant_chain_mover:
                chain_move = renderers.format_percent(significant_chain_mover["day_change"])
                chain_name = significant_chain_mover["chain"]
                sections.append(
                    {
                        "title": "Liquidity Readout",
                        "summary": (
                            f"Stablecoin balances did not show a broad system-wide expansion or contraction. The clearest move was on {chain_name} "
                            f"at {chain_move} day over day, which reads more like chain-specific liquidity repositioning than a market-wide stablecoin impulse."
                        ),
                    }
                )
            else:
                sections.append(
                    {
                        "title": "Liquidity Readout",
                        "summary": (
                            "Stablecoin supply looked relatively steady at the top level. That limits the evidence for a fresh broad-based liquidity regime shift "
                            "in this run and puts more weight on chain-specific or protocol-specific changes instead."
                        ),
                    }
                )

        risk_sentences: list[str] = []
        if yield_rows:
            risk_sentences.append(
                "Yield outliers remain the highest-noise, highest-risk slice in the report, so they should be treated as review triggers rather than attractive opportunities."
            )
        repeated_count = sum(1 for row in sec_rows if row["topic"] == "Repeated boilerplate")
        if sec_rows:
            if repeated_count and repeated_count == len(sec_rows):
                risk_sentences.append(
                    "The SEC watchlist mostly resolved to repeated crypto disclosure language, which is useful context but not strong evidence of a fresh disclosure wave."
                )
            elif repeated_count:
                risk_sentences.append(
                    f"The SEC watchlist was mixed: {repeated_count} retained rows looked like repeated disclosure, while the rest were more likely to reflect newer filing relevance."
                )
        if sanctions_rows:
            risk_sentences.append(
                "The OFAC section is still best read as screening coverage, not a claim about a brand-new sanctions event, but it remains operationally relevant because the address sets are large and exact-listed."
            )
        if risk_sentences:
            sections.append(
                {
                    "title": "Risk and Compliance",
                    "summary": " ".join(risk_sentences),
                }
            )

        sections.append(
            {
                "title": "What Matters Today",
                "summary": (
                    "The main human-readable takeaway is that price action looked broadly constructive inside the tracked exchange slice, while the deeper structural data "
                    "looked more stable than explosive. The strongest actionable review areas remain chain-specific liquidity moves, unusually high yield pockets, and whether any retained SEC filing language is genuinely new rather than repeated."
                ),
            }
        )
        return sections

    def _build_watchlist(
        self,
        leader: dict[str, Any] | None,
        protocol_rows: list[dict[str, str]],
        significant_chain_mover: dict[str, Any] | None,
        yield_rows: list[dict[str, str]],
        sec_rows: list[dict[str, str]],
        sanctions_rows: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        watchlist: list[dict[str, str]] = []
        if leader:
            watchlist.append(
                {
                    "priority": "Medium",
                    "item": leader["pair"],
                    "what_changed": f"Tracked-pair 24h change reached {renderers.format_percent(leader['price_change_percent_24h'], 3)} on Binance.",
                    "why_it_matters": "Short-horizon leadership diverged within the tracked exchange set.",
                    "confidence": "High",
                    "follow_up": "Check whether the move persists beyond Binance’s 24h window.",
                }
            )
        mover = next((row for row in protocol_rows if "exceeded 10%" in row["research_note"]), None)
        if mover:
            watchlist.append(
                {
                    "priority": "Medium",
                    "item": mover["protocol"],
                    "what_changed": f"Protocol TVL moved {mover['change'].split(' / ')[0].replace('1d ', '')} in 1 day with TVL at {mover['tvl']}.",
                    "why_it_matters": "A source-exposed TVL jump above 10% can indicate migration, incentives, or reclassification that requires review.",
                    "confidence": "Medium",
                    "follow_up": "Review protocol-specific catalysts and whether the move reverses on the next run.",
                }
            )
        if significant_chain_mover:
            watchlist.append(
                {
                    "priority": "Medium",
                    "item": significant_chain_mover["chain"],
                    "what_changed": f"Chain stablecoin supply changed {renderers.format_percent(significant_chain_mover['day_change'])} day over day.",
                    "why_it_matters": "Large chain-level liquidity moves can be chain-specific signals rather than broad market expansion.",
                    "confidence": "High",
                    "follow_up": "Check whether the move came from one stablecoin or multiple assets.",
                }
            )
        if yield_rows:
            first = yield_rows[0]
            watchlist.append(
                {
                    "priority": "High",
                    "item": first["pool_protocol"].split(" / ")[-1] + " on " + first["chain"],
                    "what_changed": f"Yield screen flagged {first['apy']} APY with {first['tvl']} TVL.",
                    "why_it_matters": "High APY with meaningful TVL is a potential risk signal and merits manual strategy review.",
                    "confidence": "Medium",
                    "follow_up": "Review emissions, lockups, and whether the APY is base or reward-driven.",
                }
            )
        if sec_rows:
            first = sec_rows[0]
            watchlist.append(
                {
                    "priority": first["priority"],
                    "item": f"{first['ticker']} {first['filing']}",
                    "what_changed": f"New {first['date']} filing retained after crypto-term body-text review.",
                    "why_it_matters": first["why_it_matters"],
                    "confidence": first["confidence"],
                    "follow_up": "Open the filing sections around the matched terms and confirm whether the language is new or repeated.",
                }
            )
        if sanctions_rows:
            first = sanctions_rows[0]
            count = re.search(r"(\d+)", first["crypto_relevance"])
            observed = count.group(1) if count else "multiple"
            watchlist.append(
                {
                    "priority": "High",
                    "item": first["item"],
                    "what_changed": f"Current OFAC XML parse surfaced {observed} digital-currency address records tied to this entry.",
                    "why_it_matters": "The current sanctions slice is now materially richer than the prior source-limited state.",
                    "confidence": "High",
                    "follow_up": "Re-screen counterparties and wallet lists against the refreshed exact-listed address set.",
                }
            )
        return watchlist[:6]

    def _build_limitations(self) -> list[str]:
        succeeded = [row.source for row in self.status_rows if row.status == "OK"]
        bullets = [f"Succeeded sources: {', '.join(succeeded)}."]
        if self.failures:
            bullets.append(f"Failed sources: {'; '.join(self.failures)}.")
        else:
            bullets.append("Failed sources: none in this run, although SEC and OFAC fetches were materially slower than the market and DeFi endpoints.")
        bullets.append(
            f"State availability note: {self.state_note} The prior snapshot from {self.prior_run_date or 'N/A'} was partial, so some change analysis remains source-limited even in diff-aware mode."
        )
        bullets.append(
            "Market-data scope note: the market section is limited to Binance 24-hour data for the nine tracked USDT pairs and should not be read as total market-wide activity."
        )
        bullets.append(
            f"SEC extraction limits: watchlist coverage used the SEC ticker map plus the BITF CIK override, then checked recent submissions from {self.lookback_start.isoformat()} through {self.run_date_str}; filing-text term matches can still include repeated disclosure language and require manual section review."
        )
        bullets.append(
            "OFAC manual-review note: OFAC results are exact-listed XML screening signals based mainly on digital-currency address fields and program tags, not legal conclusions or attribution judgments."
        )
        return bullets

    def persist(self, normalized_state: dict[str, Any], report: dict[str, Any]) -> dict[str, Path]:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = self.reports_dir / f"{self.run_date_str}.md"
        html_path = self.reports_dir / f"{self.run_date_str}.html"
        markdown = renderers.render_markdown(report)
        html_report = renderers.render_html(report, normalized_state)
        atomic_write_text(markdown_path, markdown)
        atomic_write_text(html_path, html_report)
        atomic_write_json(self.snapshot_path, normalized_state)
        atomic_write_json(self.state_path, normalized_state)
        return {"markdown": markdown_path, "html": html_path, "state": self.state_path, "snapshot": self.snapshot_path}

    def run(self) -> tuple[str, dict[str, Path]]:
        fetched = self.fetch_all()
        normalized_state = self.normalize(fetched)
        report = self.build_report(normalized_state)
        artifacts = self.persist(normalized_state, report)
        markdown = renderers.render_markdown(report)
        return markdown, artifacts


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the crypto market research digest pipeline.")
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace root used for durable state and generated report artifacts.",
    )
    return parser.parse_args(argv)
