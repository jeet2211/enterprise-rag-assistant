from app.rag.chunker import Chunker


def test_chunker_splits_large_page_with_overlap():
    text = "".join(chr(65 + (index % 26)) for index in range(280))
    chunker = Chunker(chunk_size=220, chunk_overlap=40)

    chunks = chunker.chunk_page(text, page_number=4)

    assert len(chunks) == 2
    assert chunks[0].page_number == 4
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[0].text[-40:] == chunks[1].text[:40]


def test_chunker_ignores_blank_pages():
    chunker = Chunker()

    assert chunker.chunk_page("   \n\t  ", page_number=1) == []
