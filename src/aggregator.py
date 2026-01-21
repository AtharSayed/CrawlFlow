"""
src/aggregator.py
-----------------
Aggregates metrics across all processed websites.
Computes:
- Num with case studies
- Active/inactive counts
- Content length stats per section

Outputs: summary.json in metrics/
"""

import os
import json
from collections import defaultdict
from statistics import mean
from datetime import datetime
from src.utils import get_logger, load_websites

logger = get_logger(__name__)

def compute_and_save_metrics(
    processed_base_dir: str,
    metrics_dir: str,
    execution_date: datetime = None
) -> dict:
    """
    Aggregate across all processed JSONs.
    """
    websites = load_websites(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "websites.yaml"))
    all_records = []
    website_active_status = {}

    for url in websites:
        domain = url.split('//')[-1].split('/')[0]  # Simplified get_domain
        processed_path = os.path.join(processed_base_dir, f"{domain}.json")
        if os.path.isfile(processed_path):
            with open(processed_path, "r", encoding="utf-8") as f:
                records = json.load(f)
            all_records.extend(records)
            # Track per-website active status (from any record, since same)
            if records:
                website_active_status[url] = records[0]["isActive"]

    if not all_records:
        logger.warning("No processed records found for aggregation")
        return {"status": "skipped", "reason": "no_data"}

    # Metrics computation
    metrics = {
        "total_websites_processed": len(website_active_status),
        "num_websites_with_case_studies": sum(
            1 for r in all_records
            if r["section"] == "case_study" and len(r["content"]) > 0
        ),
        "active_websites": sum(1 for active in website_active_status.values() if active),
        "inactive_websites": sum(1 for active in website_active_status.values() if not active),
        "content_length_stats": defaultdict(dict)
    }

    # Per-section stats
    section_lengths = defaultdict(list)
    for r in all_records:
        if r["content"]:
            section_lengths[r["section"]].append(len(r["content"]))

    for section, lengths in section_lengths.items():
        metrics["content_length_stats"][section] = {
            "min": min(lengths),
            "max": max(lengths),
            "avg": round(mean(lengths), 2),
            "count": len(lengths)
        }

    # Save
    timestamp = (execution_date or datetime.utcnow()).isoformat() + 'Z'
    metrics["aggregation_timestamp"] = timestamp
    summary_path = os.path.join(metrics_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"Aggregation complete | {metrics['total_websites_processed']} sites | Output: {summary_path}")

    return {
        "status": "success",
        "metrics_summary": metrics,
        "output_path": summary_path
    }


if __name__ == "__main__":
    """Local test"""
    result = compute_and_save_metrics(
        processed_base_dir="../data/processed",
        metrics_dir="../data/metrics"
    )
    print(json.dumps(result, indent=2))