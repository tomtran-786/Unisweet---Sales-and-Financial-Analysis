from __future__ import annotations

import argparse
import json
from pathlib import Path

from unisweet_analysis.sales_master import build_sales_master


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Combine Customer Sales workbooks and mappings into one flat Sales master CSV."
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    result = build_sales_master(args.project_root, output_path=args.output)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
