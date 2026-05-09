#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from crypto_digest.pipeline import DigestPipeline, parse_args


def main() -> int:
    args = parse_args()
    pipeline = DigestPipeline(Path(args.workspace).resolve())
    markdown, _ = pipeline.run()
    print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
