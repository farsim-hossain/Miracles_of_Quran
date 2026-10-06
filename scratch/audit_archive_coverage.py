"""Report substantive visible HTML blocks not present in the gathered Markdown."""

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "site_archive" / "www.miracles-of-quran.com"
GATHERED = ROOT / "Miracles_of_Quran_Gathered.md"
BASE_URL = "https://www.miracles-of-quran.com/"


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def markdown_section(document: str, url: str) -> str:
    marker = f"**URL**: {url}"
    start = document.find(marker)
    if start == -1:
        return ""
    end = document.find("\n---", start)
    return document[start : len(document) if end == -1 else end]


def blocks(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "noscript", "svg", "iframe", "nav", "footer"]):
        node.decompose()
    return [
        text
        for node in soup.select("h1, h2, h3, h4, h5, h6, p, li, blockquote, td, th")
        if len(text := " ".join(node.stripped_strings)) >= 80
    ]


def main() -> None:
    document = GATHERED.read_text(encoding="utf-8")
    missing_pages: list[tuple[str, list[str]]] = []
    total = 0
    matched = 0

    for page in sorted(ARCHIVE.glob("*.html")):
        url = BASE_URL + page.name
        section = normalized(markdown_section(document, url))
        page_missing = []
        for block in blocks(page.read_text(encoding="utf-8", errors="ignore")):
            total += 1
            if normalized(block) in section:
                matched += 1
            else:
                page_missing.append(block)
        if page_missing:
            missing_pages.append((page.name, page_missing))

    print(f"Substantive visible blocks matched: {matched}/{total}")
    print(f"Pages with unmatched blocks: {len(missing_pages)}")
    for name, missing in missing_pages:
        print(f"\n{name}: {len(missing)} unmatched")
        for block in missing[:3]:
            print(f"  - {block[:240]}")


if __name__ == "__main__":
    main()
