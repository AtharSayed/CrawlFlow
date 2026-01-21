"""
src/crawler.py
--------------
Core crawling logic for fetching website content.
Designed to be called per-website (for parallel/mapped execution in Airflow).

Features:
- Rate limiting friendly
- Basic error handling & logging
- Stores raw HTML + metadata per domain
- Detects potential case study / success story pages (heuristic)
- Saves intermediate metadata for later processing steps
"""

import os
import json
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from src.utils import (
    get_logger,
    get_domain,
    rate_limited_request     # optional rate limiter decorator
)

logger = get_logger(__name__)

# --------------------------------------------------
# Configuration / Constants
# --------------------------------------------------
MAX_CASE_STUDY_PAGES = 3
MAX_INTERNAL_PAGES = 4
REQUEST_TIMEOUT = 12           # seconds
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; WebsiteContentPipeline/1.0; +https://github.com/your-org)'
}


def crawl_website(
    url: str,
    raw_base_dir: str,
    execution_date: datetime = None,
    timeout: int = REQUEST_TIMEOUT,
    max_case_studies: int = MAX_CASE_STUDY_PAGES,
    max_internal: int = MAX_INTERNAL_PAGES
) -> dict:
    """
    Crawl a single website:
      - Homepage
      - Try to find & save navbar/footer (as reference)
      - Look for case studies / success stories
      - Grab a few internal pages

    Returns: summary dict for potential downstream use / debugging
    """
    domain = get_domain(url)
    timestamp = (execution_date or datetime.utcnow()).isoformat() + 'Z'
    base_dir = os.path.join(raw_base_dir, domain)
    os.makedirs(base_dir, exist_ok=True)

    metadata = {
        'website': url,
        'domain': domain,
        'crawl_timestamp': timestamp,
        'pages': {}
    }

    logger.info(f"[{domain}] Starting crawl → {url}")

    # ── 1. Fetch homepage ───────────────────────────────────────────────────────
    homepage_path = os.path.join(base_dir, 'homepage.html')
    try:
        resp = rate_limited_request(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True
        )
        status = resp.status_code
        html = resp.text if status == 200 else ""

        with open(homepage_path, 'w', encoding='utf-8') as f:
            f.write(html)

        metadata['pages']['homepage'] = {
            'url': url,
            'status': status,
            'size_bytes': len(html),
            'timestamp': timestamp
        }

        if status != 200:
            logger.warning(f"[{domain}] Homepage returned status {status}")
            return {'status': 'partial', 'reason': f'homepage_{status}', 'metadata': metadata}

        logger.debug(f"[{domain}] Homepage saved ({len(html):,} bytes)")

    except Exception as e:
        logger.error(f"[{domain}] Failed to fetch homepage: {str(e)}", exc_info=True)
        metadata['pages']['homepage'] = {'status': 0, 'error': str(e)}
        return {'status': 'failed', 'reason': 'homepage_fetch_error', 'metadata': metadata}

    # ── 2. Parse homepage to discover other important pages ─────────────────────
    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Collect candidate links
        case_study_candidates = []
        internal_candidates = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            full_url = urljoin(url, href)

            # Skip anchors, external, javascript, etc.
            if not full_url.startswith(('http://', 'https://')):
                continue
            if '#' in href or 'javascript:' in href.lower():
                continue

            lower_href = href.lower()
            if any(kw in lower_href for kw in [
                'case-study', 'case-studies', 'success-story', 'success-stories',
                'customer-story', 'customer-stories', 'case', 'stories', '/clients/', '/work/'
            ]):
                if full_url not in case_study_candidates:
                    case_study_candidates.append(full_url)

            elif full_url.startswith(url) and full_url != url:
                if len(internal_candidates) < max_internal:
                    internal_candidates.append(full_url)

        logger.debug(f"[{domain}] Found {len(case_study_candidates)} case-study candidates "
                     f"and {len(internal_candidates)} internal pages")

        # ── 3. Fetch case studies (priority) ───────────────────────────────────────
        case_study_fetched = 0
        for i, case_url in enumerate(case_study_candidates[:max_case_studies], 1):
            try:
                case_resp = rate_limited_request(
                    case_url,
                    headers=HEADERS,
                    timeout=timeout
                )
                if case_resp.status_code == 200:
                    path = os.path.join(base_dir, f'case_study_{i:02d}.html')
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(case_resp.text)

                    metadata['pages'][f'case_study_{i:02d}'] = {
                        'url': case_url,
                        'status': case_resp.status_code,
                        'size_bytes': len(case_resp.text),
                        'timestamp': timestamp
                    }
                    case_study_fetched += 1
                    logger.debug(f"[{domain}] Saved case study {i}: {case_url}")

            except Exception as e:
                logger.warning(f"[{domain}] Failed case study {case_url}: {str(e)}")

        # ── 4. Optional: few internal pages (can be turned off for speed) ──────────
        # Currently disabled by default for performance in large-scale runs
        # Uncomment if needed for richer context

        # internal_fetched = 0
        # for i, int_url in enumerate(internal_candidates, 1):
        #     ...

        # ── 5. Save final metadata ─────────────────────────────────────────────────
        metadata_path = os.path.join(base_dir, 'metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"[{domain}] Crawl finished | "
                    f"case studies: {case_study_fetched} | homepage: {status}")

        return {
            'status': 'success',
            'case_studies_found': case_study_fetched,
            'metadata_path': metadata_path
        }

    except Exception as e:
        logger.error(f"[{domain}] Parsing / discovery phase failed: {str(e)}", exc_info=True)
        return {
            'status': 'partial',
            'reason': 'parsing_error',
            'metadata': metadata
        }


if __name__ == "__main__":
    """Quick local test / debug"""
    from src.utils import load_websites

    test_urls = load_websites("config/websites.yaml")[:2]
    for test_url in test_urls:
        result = crawl_website(
            url=test_url,
            raw_base_dir="data/raw",
            max_case_studies=2,
            max_internal=0  # skip internals for test
        )
        print(f"Result for {test_url}:")
        print(json.dumps(result, indent=2))
        print("-" * 80)