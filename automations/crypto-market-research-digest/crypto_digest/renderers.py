from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from typing import Any


def format_money(value: float | int | None) -> str:
    if value is None:
        return "N/A"
    value = float(value)
    sign = "-" if value < 0 else ""
    absolute = abs(value)
    if absolute >= 1_000_000_000_000:
        return f"{sign}${absolute / 1_000_000_000_000:,.2f}T"
    if absolute >= 1_000_000_000:
        return f"{sign}${absolute / 1_000_000_000:,.2f}B"
    if absolute >= 1_000_000:
        return f"{sign}${absolute / 1_000_000:,.2f}M"
    if absolute >= 1_000:
        return f"{sign}${absolute / 1_000:,.2f}K"
    return f"{sign}${absolute:,.2f}"


def format_price(value: float | int | None) -> str:
    if value is None:
        return "N/A"
    value = float(value)
    if value >= 1_000:
        return f"${value:,.2f}"
    if value >= 1:
        return f"${value:,.4f}"
    return f"${value:,.6f}"


def format_percent(value: float | int | None, digits: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{float(value):+.{digits}f}%"


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = [f"# Crypto & Market Research Digest — {report['run_date_utc']}", ""]

    lines.append("## 1. Executive Summary")
    for bullet in report["executive_summary"]:
        lines.append(f"- {bullet}")
    lines.append("")

    lines.append("## 1A. Analyst Readout")
    for section in report["analyst_readout"]:
        lines.append(f"- **{section['title']}:** {section['summary']}")
    lines.append("")

    lines.append("## 2. Source Fetch Status")
    source_rows = [
        [
            row["source"],
            row["status"],
            str(row["records_checked"]),
            row["notes"],
        ]
        for row in report["source_fetch_status"]
    ]
    lines.append(markdown_table(["Source", "Status", "Records / Files Checked", "Notes"], source_rows))
    lines.append("")

    lines.append("## 3. Market Pulse")
    market_rows = [
        [
            row["asset"],
            row["pair"],
            row["last_price"],
            row["change_24h"],
            row["quote_volume_24h"],
            row["note"],
        ]
        for row in report["market_pulse"]["rows"]
    ]
    lines.append(markdown_table(["Asset", "Pair", "Last Price", "24h Change", "24h Quote Volume", "Note"], market_rows))
    lines.append("")
    lines.extend(report["market_pulse"]["narrative"])
    lines.append("")

    lines.append("## 4. DeFi Fundamentals")
    lines.append("### Chain TVL")
    lines.append(markdown_table(
        ["Chain", "TVL", "1d Change", "7d Change", "Note"],
        [
            [row["chain"], row["tvl"], row["change_1d"], row["change_7d"], row["note"]]
            for row in report["defi_fundamentals"]["chains"]
        ],
    ))
    lines.append("")
    lines.append("### Protocol TVL")
    lines.append(markdown_table(
        ["Protocol", "Category", "Chain", "TVL", "Change", "Research Note"],
        [
            [
                row["protocol"],
                row["category"],
                row["chain"],
                row["tvl"],
                row["change"],
                row["research_note"],
            ]
            for row in report["defi_fundamentals"]["protocols"]
        ],
    ))
    lines.append("")
    lines.append("### Fees and Revenue")
    lines.append(markdown_table(
        ["Protocol", "Fees", "Revenue", "Change", "Note"],
        [
            [row["protocol"], row["fees"], row["revenue"], row["change"], row["note"]]
            for row in report["defi_fundamentals"]["fees"]
        ],
    ))
    lines.append("")
    lines.append("### DEX Volume")
    lines.append(markdown_table(
        ["Protocol", "Volume", "Change", "Note"],
        [
            [row["protocol"], row["volume"], row["change"], row["note"]]
            for row in report["defi_fundamentals"]["dexs"]
        ],
    ))
    lines.append("")

    lines.append("## 5. Stablecoin and Liquidity Monitor")
    lines.append(markdown_table(
        ["Stablecoin / Chain", "Supply", "Change", "Note"],
        [
            [row["label"], row["supply"], row["change"], row["note"]]
            for row in report["stablecoin_monitor"]["rows"]
        ],
    ))
    lines.append("")
    lines.append(report["stablecoin_monitor"]["summary"])
    lines.append("")

    lines.append("## 6. Yield and Risk Outliers")
    lines.append(markdown_table(
        ["Pool / Protocol", "Chain", "APY", "TVL", "Reason Flagged", "Review Priority"],
        [
            [
                row["pool_protocol"],
                row["chain"],
                row["apy"],
                row["tvl"],
                row["reason_flagged"],
                row["review_priority"],
            ]
            for row in report["yield_outliers"]
        ],
    ))
    lines.append("")

    lines.append("## 7. SEC Filing Monitor")
    lines.append(markdown_table(
        ["Company", "Ticker", "Filing", "Date", "Topic", "Why It Matters", "Priority"],
        [
            [
                row["company"],
                row["ticker"],
                row["filing"],
                row["date"],
                row["topic"],
                row["why_it_matters"],
                row["priority"],
            ]
            for row in report["sec_filing_monitor"]["rows"]
        ],
    ))
    if report["sec_filing_monitor"]["empty_note"]:
        lines.append("")
        lines.append(report["sec_filing_monitor"]["empty_note"])
    lines.append("")

    lines.append("## 8. Sanctions and Compliance Monitor")
    lines.append(markdown_table(
        ["Item", "Source", "Change Type", "Crypto Relevance", "Review Priority"],
        [
            [
                row["item"],
                row["source"],
                row["change_type"],
                row["crypto_relevance"],
                row["review_priority"],
            ]
            for row in report["sanctions_monitor"]["rows"]
        ],
    ))
    lines.append("")
    lines.append("> Compliance notes are screening signals only and are not legal conclusions. Manual review is required before relying on them.")
    lines.append("")

    lines.append("## 9. Research Watchlist")
    lines.append(markdown_table(
        ["Priority", "Item", "What Changed", "Why It Matters", "Confidence", "Follow-Up"],
        [
            [
                row["priority"],
                row["item"],
                row["what_changed"],
                row["why_it_matters"],
                row["confidence"],
                row["follow_up"],
            ]
            for row in report["research_watchlist"]
        ],
    ))
    lines.append("")

    lines.append("## 10. Data Quality and Limitations")
    for bullet in report["limitations"]:
        lines.append(f"- {bullet}")
    return "\n".join(lines).rstrip() + "\n"


def _svg_bar_chart(
    title: str,
    data: list[tuple[str, float]],
    *,
    width: int = 640,
    height: int = 240,
    positive_color: str = "#1f8f55",
    negative_color: str = "#c23b22",
    currency: bool = False,
) -> str:
    if not data:
        return ""
    left = 140
    right = width - 30
    top = 35
    row_height = (height - top - 20) / len(data)
    values = [abs(value) for _, value in data]
    max_value = max(values) or 1.0
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        f'<text x="0" y="18" font-size="16" font-weight="700" fill="#0f172a">{html.escape(title)}</text>',
    ]
    for index, (label, value) in enumerate(data):
        y = top + index * row_height
        bar_width = (abs(value) / max_value) * (right - left)
        color = positive_color if value >= 0 else negative_color
        parts.append(
            f'<text x="0" y="{y + 16:.1f}" font-size="12" fill="#334155">{html.escape(label)}</text>'
        )
        parts.append(
            f'<rect x="{left}" y="{y + 2:.1f}" width="{bar_width:.1f}" height="18" rx="4" fill="{color}" opacity="0.85"></rect>'
        )
        display = format_money(value) if currency else format_percent(value)
        parts.append(
            f'<text x="{left + bar_width + 8:.1f}" y="{y + 16:.1f}" font-size="12" fill="#0f172a">{html.escape(display)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def _price_label(value: float | None) -> str:
    if value is None:
        return "N/A"
    if value >= 1000:
        return f"${value:,.0f}"
    if value >= 100:
        return f"${value:,.2f}"
    if value >= 1:
        return f"${value:,.3f}"
    return f"${value:,.5f}"


def _svg_candlestick_chart(
    title: str,
    candles: list[dict[str, Any]],
    *,
    width: int = 640,
    height: int = 260,
) -> str:
    if not candles:
        return ""
    top = 24
    bottom = height - 28
    left = 14
    right = width - 14
    chart_top = top + 8
    all_highs = [c["high"] for c in candles if c.get("high") is not None]
    all_lows = [c["low"] for c in candles if c.get("low") is not None]
    if not all_highs or not all_lows:
        return ""
    max_price = max(all_highs)
    min_price = min(all_lows)
    span = max(max_price - min_price, max_price * 0.002, 1e-9)
    inner_width = right - left
    candle_width = max(4.0, inner_width / max(len(candles), 1) * 0.55)
    step = inner_width / max(len(candles), 1)

    def y_for(price: float) -> float:
        return chart_top + (max_price - price) / span * (bottom - chart_top)

    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        f'<text x="0" y="18" font-size="16" font-weight="700" fill="#0f172a">{html.escape(title)}</text>',
    ]
    for guide in range(3):
        guide_price = max_price - span * guide / 2
        y = y_for(guide_price)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#d8cfbf" stroke-width="1"></line>')
        parts.append(f'<text x="{right - 2}" y="{y - 4:.1f}" font-size="11" text-anchor="end" fill="#5e6678">{html.escape(_price_label(guide_price))}</text>')

    for index, candle in enumerate(candles):
        if None in (candle.get("open"), candle.get("high"), candle.get("low"), candle.get("close")):
            continue
        open_price = float(candle["open"])
        high_price = float(candle["high"])
        low_price = float(candle["low"])
        close_price = float(candle["close"])
        x_center = left + step * index + step / 2
        wick_top = y_for(high_price)
        wick_bottom = y_for(low_price)
        body_top = y_for(max(open_price, close_price))
        body_bottom = y_for(min(open_price, close_price))
        color = "#1f8f55" if close_price >= open_price else "#c23b22"
        body_height = max(2.0, body_bottom - body_top)
        body_y = body_top if body_height > 2.0 else body_top - 1.0
        parts.append(f'<line x1="{x_center:.1f}" y1="{wick_top:.1f}" x2="{x_center:.1f}" y2="{wick_bottom:.1f}" stroke="{color}" stroke-width="1.5"></line>')
        parts.append(
            f'<rect x="{x_center - candle_width / 2:.1f}" y="{body_y:.1f}" width="{candle_width:.1f}" height="{body_height:.1f}" rx="1.5" fill="{color}" opacity="0.9"></rect>'
        )

    first_ts = candles[0].get("open_time_ms")
    last_ts = candles[-1].get("close_time_ms")
    if first_ts and last_ts:
        first_label = datetime.fromtimestamp(first_ts / 1000, tz=timezone.utc).strftime("%H:%M")
        last_label = datetime.fromtimestamp(last_ts / 1000, tz=timezone.utc).strftime("%H:%M")
        parts.append(f'<text x="{left}" y="{height - 6}" font-size="11" fill="#5e6678">{html.escape(first_label)} UTC</text>')
        parts.append(f'<text x="{right}" y="{height - 6}" font-size="11" text-anchor="end" fill="#5e6678">{html.escape(last_label)} UTC</text>')
    parts.append("</svg>")
    return "".join(parts)


def render_html(report: dict[str, Any], normalized_state: dict[str, Any]) -> str:
    featured_candles = normalized_state.get("featured_candles", {})
    candle_svgs = []
    for symbol in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
        candles = featured_candles.get(symbol, [])
        svg = _svg_candlestick_chart(f"{symbol} {len(candles)}x1h Candles", candles)
        if svg:
            candle_svgs.append(
                "<section>"
                + svg
                + f'<div class="caption">{html.escape(symbol.replace("USDT", "") + " short-horizon price structure over the latest hourly window.")}</div>'
                + "</section>"
            )
    market_chart_data = [
        (row["asset"], row["change_value_24h"])
        for row in report["market_pulse"]["rows"]
    ]
    chain_tvl_chart_data = [
        (row["name"], row["tvl"])
        for row in normalized_state.get("defi", {}).get("chains", [])[:5]
        if row.get("tvl") is not None
    ]
    dex_volume_chart_data = [
        (row["protocol"], row["volume"])
        for row in normalized_state.get("defi", {}).get("dexs", [])[:5]
        if row.get("volume") is not None
    ]
    stablecoin_chart_data = [
        (row["label"], row["change_value_day"])
        for row in report["stablecoin_monitor"]["rows"]
        if row["change_value_day"] is not None
    ][:5]
    market_svg = _svg_bar_chart("Tracked Pair 24h Change", market_chart_data)
    chain_tvl_svg = _svg_bar_chart("Top Chain TVL", chain_tvl_chart_data, currency=True)
    dex_volume_svg = _svg_bar_chart("Top DEX 24h Volume", dex_volume_chart_data, currency=True)
    stablecoin_svg = _svg_bar_chart("Chain Stablecoin 1d Change", stablecoin_chart_data)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    def table_html(headers: list[str], rows: list[list[str]]) -> str:
        head = "".join(f"<th>{html.escape(cell)}</th>" for cell in headers)
        body_rows = []
        for row in rows:
            body_rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
        return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"

    source_rows = [
        [
            html.escape(row["source"]),
            html.escape(row["status"]),
            str(row["records_checked"]),
            html.escape(row["notes"]),
        ]
        for row in report["source_fetch_status"]
    ]
    market_rows = [
        [
            html.escape(row["asset"]),
            html.escape(row["pair"]),
            html.escape(row["last_price"]),
            f'<span class="pill {"positive" if row["change_value_24h"] >= 0 else "negative"}">{html.escape(row["change_24h"])}</span>',
            html.escape(row["quote_volume_24h"]),
            html.escape(row["note"]),
        ]
        for row in report["market_pulse"]["rows"]
    ]
    stablecoin_rows = [
        [
            html.escape(row["label"]),
            html.escape(row["supply"]),
            html.escape(row["change"]),
            html.escape(row["note"]),
        ]
        for row in report["stablecoin_monitor"]["rows"]
    ]
    watchlist_rows = [
        [
            html.escape(row["priority"]),
            html.escape(row["item"]),
            html.escape(row["what_changed"]),
            html.escape(row["why_it_matters"]),
            html.escape(row["confidence"]),
            html.escape(row["follow_up"]),
        ]
        for row in report["research_watchlist"]
    ]
    executive_cards = "".join(
        f"<li>{html.escape(item)}</li>" for item in report["executive_summary"]
    )
    insight_cards = "".join(
        (
            '<article class="insight-card">'
            f"<h3>{html.escape(section['title'])}</h3>"
            f"<p>{html.escape(section['summary'])}</p>"
            "</article>"
        )
        for section in report["analyst_readout"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Crypto &amp; Market Research Digest — {html.escape(report['run_date_utc'])}</title>
  <style>
    :root {{
      --bg: #f5f3ee;
      --panel: #fffaf3;
      --ink: #172033;
      --muted: #5e6678;
      --border: #d8cfbf;
      --accent: #0c7c59;
      --accent-2: #ca6b2c;
      --danger: #b9381f;
      --shadow: 0 18px 40px rgba(23, 32, 51, 0.08);
      --mono: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
      --sans: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, Georgia, serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(202, 107, 44, 0.10), transparent 28%),
        linear-gradient(180deg, #f8f5ef 0%, var(--bg) 100%);
      color: var(--ink);
      font-family: var(--sans);
      line-height: 1.5;
    }}
    .page {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}
    .hero {{
      display: grid;
      gap: 18px;
      margin-bottom: 24px;
    }}
    .eyebrow {{
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--accent-2);
      font-size: 12px;
      font-weight: 700;
    }}
    h1, h2, h3 {{
      margin: 0;
      font-weight: 700;
      line-height: 1.15;
    }}
    h1 {{ font-size: clamp(34px, 6vw, 56px); }}
    h2 {{ font-size: 26px; margin-bottom: 12px; }}
    h3 {{ font-size: 18px; margin-bottom: 10px; }}
    p, li {{ color: var(--ink); }}
    .meta {{
      color: var(--muted);
      font-size: 14px;
    }}
    .grid {{
      display: grid;
      gap: 18px;
    }}
    .cards {{
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      margin-bottom: 22px;
    }}
    .charts {{
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      margin-bottom: 18px;
    }}
    .card, .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
      border-radius: 18px;
    }}
    .card {{
      padding: 18px;
    }}
    .card .label {{
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .card .value {{
      margin-top: 8px;
      font-size: 28px;
      font-weight: 700;
    }}
    .panel {{
      padding: 22px;
      margin-bottom: 18px;
    }}
    .insight-grid {{
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }}
    .insight-card {{
      background: rgba(12, 124, 89, 0.05);
      border: 1px solid rgba(12, 124, 89, 0.16);
      border-radius: 14px;
      padding: 16px;
    }}
    .insight-card h3 {{
      margin-bottom: 8px;
      font-size: 17px;
    }}
    .insight-card p {{
      margin: 0;
      font-size: 14px;
      color: var(--ink);
    }}
    ul {{
      margin: 0;
      padding-left: 20px;
    }}
    .two-up {{
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
      margin-top: 8px;
    }}
    th, td {{
      padding: 10px 10px;
      text-align: left;
      vertical-align: top;
      border-bottom: 1px solid var(--border);
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .pill {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      background: rgba(12, 124, 89, 0.10);
      color: var(--accent);
    }}
    .pill.negative {{
      background: rgba(185, 56, 31, 0.10);
      color: var(--danger);
    }}
    .pill.positive {{
      background: rgba(12, 124, 89, 0.10);
      color: var(--accent);
    }}
    .caption {{
      color: var(--muted);
      font-size: 13px;
      margin-top: 8px;
    }}
    pre {{
      margin: 0;
      overflow: auto;
      font-size: 12px;
      background: #efe8dc;
      border-radius: 12px;
      padding: 14px;
      border: 1px solid var(--border);
      font-family: var(--mono);
    }}
    .footer-note {{
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 700px) {{
      .page {{ padding: 20px 14px 40px; }}
      .panel, .card {{ border-radius: 14px; }}
      table {{ font-size: 13px; }}
      th, td {{ padding: 8px 6px; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div class="eyebrow">Static Daily Research Artifact</div>
      <h1>Crypto &amp; Market Research Digest</h1>
      <div class="meta">Run date: {html.escape(report['run_date_utc'])} · Generated: {generated_at} · Mode: {html.escape(report['mode'])}</div>
    </section>

    <section class="grid cards">
      <article class="card">
        <div class="label">Tracked Pair Leader</div>
        <div class="value">{html.escape(report['summary_cards']['market_leader'])}</div>
      </article>
      <article class="card">
        <div class="label">Top Chain TVL</div>
        <div class="value">{html.escape(report['summary_cards']['top_chain'])}</div>
      </article>
      <article class="card">
        <div class="label">SEC Rows</div>
        <div class="value">{html.escape(str(report['summary_cards']['sec_rows']))}</div>
      </article>
      <article class="card">
        <div class="label">OFAC Exact Crypto Addresses</div>
        <div class="value">{html.escape(str(report['summary_cards']['ofac_rows']))}</div>
      </article>
    </section>

    <section class="panel">
      <h2>Executive Summary</h2>
      <ul>{executive_cards}</ul>
    </section>

    <section class="panel">
      <h2>Analyst Readout</h2>
      <div class="insight-grid">{insight_cards}</div>
    </section>

    <section class="panel">
      <h2>Visual Signals</h2>
      <div class="grid charts">
        {''.join(candle_svgs)}
        <section>{market_svg}<div class="caption">{html.escape(" ".join(report["market_pulse"]["narrative"]))}</div></section>
        <section>{chain_tvl_svg}<div class="caption">Top chain TVL remains concentrated in the largest settlement and smart-contract venues rather than rotating into the long tail.</div></section>
        <section>{stablecoin_svg}<div class="caption">{html.escape(report["stablecoin_monitor"]["summary"])}</div></section>
        <section>{dex_volume_svg}<div class="caption">DEX activity remains concentrated in a small group of venues, which helps separate broad onchain participation from isolated protocol spikes.</div></section>
      </div>
    </section>

    <section class="grid two-up">
      <section class="panel">
        <h2>Market Snapshot</h2>
        <div class="caption">{html.escape(" ".join(report["market_pulse"]["narrative"]))}</div>
      </section>
      <section class="panel">
        <h2>Stablecoin Liquidity</h2>
        <div class="caption">{html.escape(report["stablecoin_monitor"]["summary"])}</div>
      </section>
    </section>

    <section class="panel">
      <h2>Source Fetch Status</h2>
      {table_html(["Source", "Status", "Records / Files Checked", "Notes"], source_rows)}
    </section>

    <section class="panel">
      <h2>Market Pulse Table</h2>
      {table_html(["Asset", "Pair", "Last Price", "24h Change", "24h Quote Volume", "Note"], market_rows)}
    </section>

    <section class="grid two-up">
      <section class="panel">
        <h2>Stablecoin Monitor</h2>
        {table_html(["Stablecoin / Chain", "Supply", "Change", "Note"], stablecoin_rows)}
      </section>
      <section class="panel">
        <h2>Research Watchlist</h2>
        {table_html(["Priority", "Item", "What Changed", "Why It Matters", "Confidence", "Follow-Up"], watchlist_rows)}
      </section>
    </section>

  </div>
</body>
</html>
"""
