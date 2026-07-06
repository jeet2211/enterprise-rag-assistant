from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Chunk:
    text: str
    page_number: int
    chunk_index: int
    token_count: int  # approximate word-token count
    section_title: str = ""


class Chunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.chunk_size = max(200, chunk_size)
        self.chunk_overlap = max(0, min(chunk_overlap, self.chunk_size - 1))

    def chunk_page(self, text: str, page_number: int, section_title: str = "") -> list[Chunk]:
        normalized = " ".join(text.split())
        tokens = normalized.split()
        if not tokens:
            return []

        chunks: list[Chunk] = []
        start = 0
        chunk_index = 0
        length = len(tokens)
        while start < length:
            end = min(length, start + self.chunk_size)
            chunk_tokens = tokens[start:end]
            if chunk_tokens:
                chunk_text = " ".join(chunk_tokens).strip()
                token_count = len(chunk_tokens)
                chunks.append(
                    Chunk(
                        text=chunk_text,
                        page_number=page_number,
                        chunk_index=chunk_index,
                        token_count=token_count,
                        section_title=section_title,
                    )
                )
            if end >= length:
                break
            start = max(end - self.chunk_overlap, start + 1)
            chunk_index += 1
        return chunks

    def chunk_pages(self, pages: list[tuple[int, str, str]]) -> list[Chunk]:
        items: list[Chunk] = []
        for page_number, text, section_title in pages:
            items.extend(self.chunk_page(text, page_number, section_title))
        return items
