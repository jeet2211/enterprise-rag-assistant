from __future__ import annotations

from dataclasses import dataclass

import fitz


@dataclass(slots=True)
class PageText:
    page_number: int
    text: str


class PDFService:
    def extract_pages(self, file_path: str) -> list[PageText]:
        pages: list[PageText] = []
        with fitz.open(file_path) as doc:
            for index in range(doc.page_count):
                page = doc.load_page(index)
                text = page.get_text("text").strip()
                pages.append(PageText(page_number=index + 1, text=text))
        return pages

