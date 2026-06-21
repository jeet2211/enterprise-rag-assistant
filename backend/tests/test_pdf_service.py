from app.services.pdf_service import PDFService


class FakePage:
    def __init__(self, text: str):
        self._text = text

    def get_text(self, mode: str):
        assert mode == "text"
        return self._text


class FakeDoc:
    def __init__(self, pages: list[str]):
        self.pages = pages
        self.page_count = len(pages)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def load_page(self, index: int):
        return FakePage(self.pages[index])


def test_pdf_service_extract_pages(monkeypatch):
    fake_doc = FakeDoc(["First page", "Second page"])
    monkeypatch.setattr("app.services.pdf_service.fitz.open", lambda file_path: fake_doc)

    pages = PDFService().extract_pages("/tmp/example.pdf")

    assert [page.page_number for page in pages] == [1, 2]
    assert [page.text for page in pages] == ["First page", "Second page"]
