from __future__ import annotations

from dataclasses import dataclass
import re

import fitz


@dataclass(slots=True)
class PageText:
    page_number: int
    text: str
    section_title: str = ""


def _detect_section_title(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""

    heading_patterns = [
        r"^(?:\d+(?:\.\d+){0,4})\s+(.+)$",
        r"^(?:chapter|section)\s+\d*[:.\-]?\s*(.+)$",
    ]

    for line in lines[:8]:
        if len(line) <= 120:
            if line.isupper() and len(line.split()) <= 12:
                return line.title()
            for pattern in heading_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    candidate = match.group(1).strip(" :-")
                    return candidate[:120]

    for line in lines[:4]:
        if len(line.split()) <= 12 and len(line) <= 90:
            return line[:120]

    return ""


class PDFService:
    def extract_pages(self, file_path: str) -> list[PageText]:
        pages: list[PageText] = []
        try:
            doc = fitz.open(file_path)
        except fitz.FileDataError as exc:
            raise ValueError(f"invalid_pdf: Could not open PDF file. It may be corrupted or not a valid PDF. Detail: {exc}") from exc

        with doc:
            # Detect password-protected PDFs
            if doc.needs_pass:
                raise ValueError("password_protected_pdf: This PDF is password-protected. Please provide an unlocked PDF.")

            if doc.page_count == 0:
                raise ValueError("empty_pdf: The uploaded PDF has no pages.")

            total_text = 0
            for index in range(doc.page_count):
                page = doc.load_page(index)
                text = page.get_text("text").strip()
                total_text += len(text)
                pages.append(PageText(page_number=index + 1, text=text, section_title=_detect_section_title(text)))

            if total_text == 0:
                raise ValueError("no_extractable_text: This PDF appears to contain only images or scanned content with no extractable text. Please use a text-based PDF.")

        return pages
