"""
src/extractor.py
----------------
Extracts and categorizes meaningful sections from raw HTML files saved by the crawler.

Supported sections:
- navbar
- footer
- homepage (main content, cleaned)
- case_study (combined from all found case study pages)

Output: JSON file with extracted clean text per section
"""

import os
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup, Comment

from src.utils import get_logger, get_domain

logger = get_logger(__name__)

# --------------------------------------------------
# Extraction heuristics / patterns
# --------------------------------------------------
NAVBAR_PATTERNS = [
    r'(?i)nav|menu|header-nav|topbar|main-menu|navbar|navigation',
    r'(?i)site-header|global-nav|primary-nav'
]

FOOTER_PATTERNS = [
    r'(?i)footer|site-footer|bottom|copyright|legal-links'
]

MAIN_CONTENT_PATTERNS = [
    r'(?i)main|content|article|primary|page-content|body-main',
    r'(?i)hero|section-content|main-content'
]


def clean_text(text: str) -> str:
    """Basic text cleaning: remove extra whitespace, scripts, comments, etc."""
    if not text:
        return ""
    
    # Remove multiple spaces, newlines, tabs
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove zero-width spaces & similar
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    return text


def extract_section_from_html(html: str, section_type: str) -> str:
    """
    Try to extract meaningful content for a given section type using heuristics.
    Returns cleaned text or empty string if nothing meaningful found.
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, 'html.parser')

    # Remove unwanted elements first
    for elem in soup(["script", "style", "noscript", "iframe", "form"]):
        elem.decompose()
    
    # Remove HTML comments
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    text = ""

    if section_type == "navbar":
        # 1. Try semantic <nav> tag
        nav = soup.find("nav")
        if nav:
            text = nav.get_text(separator=" ", strip=True)
        
        # 2. Fallback: look for classes/ids matching patterns
        if not text:
            for pattern in NAVBAR_PATTERNS:
                candidate = soup.find(class_=re.compile(pattern)) or \
                            soup.find(id=re.compile(pattern))
                if candidate:
                    text = candidate.get_text(separator=" ", strip=True)
                    break

    elif section_type == "footer":
        footer = soup.find("footer")
        if footer:
            text = footer.get_text(separator=" ", strip=True)
        else:
            for pattern in FOOTER_PATTERNS:
                candidate = soup.find(class_=re.compile(pattern)) or \
                            soup.find(id=re.compile(pattern))
                if candidate:
                    text = candidate.get_text(separator=" ", strip=True)
                    break

    elif section_type == "homepage":
        # Try semantic <main>
        main = soup.find("main")
        if main:
            text = main.get_text(separator=" ", strip=True)
        else:
            # Fallback: body minus known nav/header/footer
            body = soup.find("body")
            if body:
                for unwanted in body.find_all(["nav", "header", "footer"]):
                    unwanted.decompose()
                text = body.get_text(separator=" ", strip=True)

        # Last resort: biggest content block by heuristics
        if len(text) < 300 and soup.body:
            candidates = soup.body.find_all(class_=re.compile(r'(?i)content|main|article'))
            if candidates:
                biggest = max(candidates, key=lambda x: len(x.get_text(strip=True)))
                text = biggest.get_text(separator=" ", strip=True)

    elif section_type == "case_study":
        # For case studies we usually take most of the body content
        main = soup.find("main") or soup.find("article") or soup.body
        if main:
            # Remove common noise
            for elem in main.find_all(["nav", "header", "footer", "aside", "form"]):
                elem.decompose()
            text = main.get_text(separator=" ", strip=True)
        else:
            text = soup.get_text(separator=" ", strip=True)

    return clean_text(text)


def extract_and_tag(
    url: str,
    raw_base_dir: str,
    execution_date: datetime = None
) -> dict:
    """
    Main entry point - extract sections for one website
    Input: url (used to find the domain folder)
    Output: summary for logging / downstream
    """
    domain = get_domain(url)
    base_dir = os.path.join(raw_base_dir, domain)

    if not os.path.isdir(base_dir):
        logger.warning(f"[{domain}] Raw directory not found: {base_dir}")
        return {"status": "skipped", "reason": "no_raw_data"}

    timestamp = (execution_date or datetime.utcnow()).isoformat() + 'Z'
    extracted = {
        "website": url,
        "domain": domain,
        "crawl_timestamp": timestamp,
        "sections": {}
    }

    logger.info(f"[{domain}] Starting content extraction")

    # 1. Homepage (always present)
    homepage_path = os.path.join(base_dir, "homepage.html")
    if os.path.isfile(homepage_path):
        with open(homepage_path, "r", encoding="utf-8") as f:
            html = f.read()
        extracted["sections"]["homepage"] = extract_section_from_html(html, "homepage")

    # 2. Navbar & Footer (we use homepage HTML as reference)
    if "homepage" in extracted["sections"] and extracted["sections"]["homepage"]:
        html = open(homepage_path, "r", encoding="utf-8").read()  # reread or keep in memory
        extracted["sections"]["navbar"] = extract_section_from_html(html, "navbar")
        extracted["sections"]["footer"] = extract_section_from_html(html, "footer")

    # 3. Case studies (combine multiple pages)
    case_content = []
    i = 1
    while True:
        case_path = os.path.join(base_dir, f"case_study_{i:02d}.html")
        if not os.path.isfile(case_path):
            break
        with open(case_path, "r", encoding="utf-8") as f:
            html = f.read()
        page_text = extract_section_from_html(html, "case_study")
        if page_text:
            case_content.append(page_text)
        i += 1

    if case_content:
        extracted["sections"]["case_study"] = " ".join(case_content)

    # Save extracted content
    extracted_path = os.path.join(base_dir, "extracted.json")
    with open(extracted_path, "w", encoding="utf-8") as f:
        json.dump(extracted, f, indent=2, ensure_ascii=False)

    section_count = len([s for s in extracted["sections"].values() if s])
    logger.info(f"[{domain}] Extraction done | {section_count} meaningful sections found")

    return {
        "status": "success",
        "sections_extracted": list(extracted["sections"].keys()),
        "output_path": extracted_path
    }


if __name__ == "__main__":
    """Quick local test"""
    from src.utils import load_websites

    test_urls = load_websites("../config/websites.yaml")[:1]
    for url in test_urls:
        result = extract_and_tag(url=url, raw_base_dir="../data/raw")
        print(f"Extraction result for {url}:")
        print(json.dumps(result, indent=2))