from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from unisweet_analysis.analysis import build_analysis_pack
from unisweet_analysis.config import ProjectPaths, load_json
from unisweet_analysis.loaders import (
    load_mappings,
    load_market,
    load_pnl,
    load_sales,
    source_records,
)
from unisweet_analysis.publish import (
    publish_presentation,
    write_json,
    write_story_review,
)


def run_analysis(
    project_root: Path,
    *,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    paths = ProjectPaths.from_root(project_root, output_dir)
    settings = load_json(paths.settings_file)
    story = load_json(paths.story_file)
    paths.output_dir.mkdir(parents=True, exist_ok=True)

    raw_sales, sales_sources = load_sales(paths, settings)
    customers, brands, products, mapping_source = load_mappings(paths)
    pnl, pnl_source = load_pnl(paths)
    market, market_source = load_market(paths)
    sources = [*sales_sources, mapping_source, pnl_source, market_source]

    pack = build_analysis_pack(
        project_name=settings["project_name"],
        raw_sales=raw_sales,
        customers=customers,
        brands=brands,
        products=products,
        pnl=pnl,
        market=market,
        source_manifest=source_records(sources),
        settings=settings,
    )

    analysis_path = paths.output_dir / settings["outputs"]["analysis_pack"]
    story_path = paths.output_dir / settings["outputs"]["story_review"]
    presentation_path = paths.output_dir / settings["outputs"]["presentation"]
    summary_path = paths.output_dir / settings["outputs"]["run_summary"]

    write_json(pack, analysis_path)
    write_story_review(pack, story, story_path)

    presentation_status = "NOT_PUBLISHED"
    if pack["metadata"]["publication_status"] == "READY":
        if story.get("status", "draft").lower() == "approved":
            publish_presentation(pack, story, presentation_path)
            presentation_status = "PUBLISHED"
        elif presentation_path.exists():
            presentation_path.unlink()
            presentation_status = "REMOVED_STALE_DRAFT"

    summary = {
        "project": settings["project_name"],
        "publication_status": pack["metadata"]["publication_status"],
        "critical_failure_count": pack["metadata"]["critical_failure_count"],
        "reporting_month": pack["metadata"]["reporting_month"],
        "comparison": f"{pack['metadata']['comparison_basis']}:{pack['metadata']['comparison_month']}",
        "input_hash": pack["metadata"]["input_hash"],
        "source_file_count": len(sources),
        "sales_source_file_count": len(sales_sources),
        "quarantine_row_count": pack["quarantine"]["row_count"],
        "insight_count": len(pack["insights"]),
        "story_status": story.get("status", "draft").upper(),
        "presentation_status": presentation_status,
        "outputs": {
            "analysis_pack": analysis_path.as_posix(),
            "story_review": story_path.as_posix(),
            "presentation": presentation_path.as_posix() if presentation_status == "PUBLISHED" else None,
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary
