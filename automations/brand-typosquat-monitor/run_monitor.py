#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from brand_monitor.pipeline import BrandTyposquatMonitorPipeline, parse_args


def main() -> int:
    args = parse_args()
    pipeline = BrandTyposquatMonitorPipeline(
        workspace=Path(args.workspace).resolve(),
        brand=args.brand,
        canonical_inputs=args.canonical,
        high_risk_terms=args.high_risk_terms,
        candidate_limit=args.candidate_limit,
    )
    markdown, _ = pipeline.run()
    print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
