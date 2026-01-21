"""
src/transformer.py
------------------
Transforms extracted sections into standardized data model records.
One record per section per website.

Standardized format example:
{
    "website": "https://example.com",
    "section": "case_study",
    "content": "Extracted text...",
    "crawl_timestamp": "2026-01-20T10:30:00Z",
    "isActive": true
}
"""

import os
import json
from datetime import datetime

from src.utils import get_logger, get_domain

logger = get_logger(__name__)

def transform_to_standard(
    url: str,
    raw_base_dir: str,
    processed_base_dir: str,
    execution_date: datetime = None
) -> dict:
    """
    Transform for one website.
    Reads extracted.json + metadata.json → produces <domain>.json in processed/
    """
    domain = get_domain(url)
    base_dir = os.path.join(raw_base_dir, domain)
    processed_path = os.path.join(processed_base_dir, f"{domain}.json")

    if not os.path.isdir(base_dir):
        logger.warning(f"[{domain}] Raw directory not found: {base_dir}")
        return {"status": "skipped", "reason": "no_raw_data"}

    # Load inputs
    extracted_path = os.path.join(base_dir, "extracted.json")
    metadata_path = os.path.join(base_dir, "metadata.json")

    if not (os.path.isfile(extracted_path) and os.path.isfile(metadata_path)):
        logger.warning(f"[{domain}] Missing extracted/metadata files")
        return {"status": "skipped", "reason": "missing_inputs"}

    with open(extracted_path, "r", encoding="utf-8") as f:
        extracted = json.load(f)

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    timestamp = (execution_date or datetime.utcnow()).isoformat() + 'Z'
    homepage_status = metadata.get("pages", {}).get("homepage", {}).get("status", 500)
    has_content = any(len(content) > 0 for content in extracted.get("sections", {}).values())
    is_active = (homepage_status == 200 and has_content)

    records = []
    for section, content in extracted.get("sections", {}).items():
        records.append({
            "website": url,
            "section": section,
            "content": content,
            "crawl_timestamp": timestamp,
            "isActive": is_active
        })

    # Save
    with open(processed_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    logger.info(f"[{domain}] Transformed {len(records)} records | isActive: {is_active}")

    return {
        "status": "success",
        "records_count": len(records),
        "output_path": processed_path
    }


if __name__ == "__main__":
    """Local test"""
    from src.utils import load_websites

    test_urls = load_websites("../config/websites.yaml")[:1]
    for url in test_urls:
        result = transform_to_standard(
            url=url,
            raw_base_dir="../data/raw",
            processed_base_dir="../data/processed"
        )
        print(json.dumps(result, indent=2))