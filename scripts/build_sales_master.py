from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from unisweet_analysis.sales_master_cli import main as cli_main


def main() -> int:
    return cli_main(["--project-root", str(PROJECT_ROOT), *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
