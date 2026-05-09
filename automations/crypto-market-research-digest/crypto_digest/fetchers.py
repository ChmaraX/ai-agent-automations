from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import gzip
import zlib
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from . import config


class FetchError(RuntimeError):
    """Raised when a public source cannot be fetched or parsed."""


def _read_response_bytes(response: Any) -> bytes:
    raw = response.read()
    encoding = (response.headers.get("Content-Encoding") or "").lower()
    if encoding == "gzip":
        return gzip.decompress(raw)
    if encoding == "deflate":
        return zlib.decompress(raw)
    return raw


def fetch_json(url: str, *, headers: dict[str, str] | None = None, timeout: int = 60) -> Any:
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(_read_response_bytes(response).decode("utf-8"))
    except Exception as exc:  # pragma: no cover - network failure surfaces in runtime usage
        raise FetchError(f"{url}: {exc}") from exc


def fetch_text(url: str, *, headers: dict[str, str] | None = None, timeout: int = 60) -> str:
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return _read_response_bytes(response).decode("utf-8", errors="ignore")
    except Exception as exc:  # pragma: no cover - network failure surfaces in runtime usage
        raise FetchError(f"{url}: {exc}") from exc


def fetch_bytes(url: str, *, headers: dict[str, str] | None = None, timeout: int = 60) -> bytes:
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return _read_response_bytes(response)
    except Exception as exc:  # pragma: no cover - network failure surfaces in runtime usage
        raise FetchError(f"{url}: {exc}") from exc


def fetch_binance_pairs(symbols: list[str]) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(
        {"symbols": json.dumps(symbols, separators=(",", ":"))}
    )
    url = f"{config.BINANCE_ENDPOINT}?{query}"
    try:
        data = fetch_json(url, timeout=45)
        if isinstance(data, list) and len(data) == len(symbols):
            return data
    except FetchError:
        pass

    rows = []
    for symbol in symbols:
        row = fetch_json(
            f"{config.BINANCE_ENDPOINT}?{urllib.parse.urlencode({'symbol': symbol})}",
            timeout=45,
        )
        rows.append(row)
    return rows


def fetch_binance_klines(symbol: str, *, interval: str, limit: int) -> list[list[Any]]:
    query = urllib.parse.urlencode({"symbol": symbol, "interval": interval, "limit": str(limit)})
    return fetch_json(f"{config.BINANCE_KLINES_ENDPOINT}?{query}", timeout=45)


def fetch_sec_ticker_map(cache_root: Path) -> tuple[dict[str, Any], bool]:
    cache_root.mkdir(parents=True, exist_ok=True)
    cache_path = cache_root / config.SEC_TICKER_CACHE_FILENAME
    now = time.time()
    if cache_path.exists() and now - cache_path.stat().st_mtime <= config.SEC_TICKER_CACHE_TTL_SECONDS:
        try:
            return json.loads(cache_path.read_text()), True
        except json.JSONDecodeError:
            pass

    data = fetch_json(config.SEC_TICKERS, headers={"User-Agent": config.SEC_USER_AGENT}, timeout=60)
    cache_path.write_text(json.dumps(data))
    return data, False


def fetch_sec_submission(cik: str) -> dict[str, Any]:
    return fetch_json(
        config.SEC_SUBMISSIONS.format(cik=cik),
        headers={"User-Agent": config.SEC_USER_AGENT, "Accept-Encoding": "gzip, deflate"},
        timeout=60,
    )


def fetch_sec_filing_text(cik: str, accession_number: str, primary_document: str) -> str:
    accession_compact = accession_number.replace("-", "")
    cik_no_leading_zeroes = str(int(cik))
    url = (
        "https://www.sec.gov/Archives/edgar/data/"
        f"{cik_no_leading_zeroes}/{accession_compact}/{primary_document}"
    )
    return fetch_text(
        url,
        headers={"User-Agent": config.SEC_USER_AGENT, "Accept-Encoding": "gzip, deflate"},
        timeout=75,
    )


def fetch_ofac_tree(url: str) -> ElementTree.Element:
    raw = fetch_bytes(url, timeout=90)
    try:
        return ElementTree.fromstring(raw)
    except ElementTree.ParseError as exc:  # pragma: no cover - runtime failure
        raise FetchError(f"{url}: {exc}") from exc
