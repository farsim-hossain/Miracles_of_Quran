"""Insert substantive visible source text missing from the gathered Markdown.

This deliberately inserts only text blocks that the prior extractor omitted; it does
not rewrite existing sections or add recurring navigation/footer boilerplate.
"""

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


def source_blocks(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "noscript", "svg", "iframe", "nav", "footer"]):
        node.decompose()
    return [
        text
        for node in soup.select("h1, h2, h3, h4, h5, h6, p, li, blockquote, td, th")
        if len(text := " ".join(node.stripped_strings)) >= 80
    ]


def section_bounds(document: str, url: str) -> tuple[int, int] | None:
    marker = f"**URL**: {url}"
    start = document.find(marker)
    if start == -1:
        return None
    end = document.find("\n---", start)
    return start, len(document) if end == -1 else end


def main() -> None:
    document = GATHERED.read_text(encoding="utf-8")
    restored_pages = 0
    restored_blocks = 0

    # Work backwards so offsets earlier in the document stay valid.
    for page in sorted(ARCHIVE.glob("*.html"), reverse=True):
        url = BASE_URL + page.name
        bounds = section_bounds(document, url)
        if bounds is None:
            continue
        start, end = bounds
        section = document[start:end]
        present = normalized(section)
        missing = [block for block in source_blocks(page.read_text(encoding="utf-8", errors="ignore")) if normalized(block) not in present]
        if not missing:
            continue

        addition = "\n\n#### Source text restored from the complete local archive\n\n"
        addition += "\n\n".join(f"> {block}" for block in missing)
        document = document[:end] + addition + document[end:]
        restored_pages += 1
        restored_blocks += len(missing)

    if restored_blocks:
        GATHERED.write_text(document, encoding="utf-8")
    print(f"Restored {restored_blocks} text blocks across {restored_pages} pages.")


if __name__ == "__main__":
    main()
