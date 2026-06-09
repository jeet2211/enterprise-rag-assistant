from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from sqlalchemy import select

from app.models.db import Document


class DocumentService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create_document(self, *, document_id: str, filename: str, file_path: str, file_size: int) -> Document:
        with self.session_factory() as session:
            row = Document(
                id=document_id,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                status="processing",
                uploaded_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return row

    def list_documents(self) -> list[Document]:
        with self.session_factory() as session:
            stmt = select(Document).order_by(Document.uploaded_at.desc())
            return list(session.scalars(stmt).all())

    def get_document(self, document_id: str) -> Document | None:
        with self.session_factory() as session:
            return session.get(Document, document_id)

    def update_document(
        self,
        document_id: str,
        *,
        status: str | None = None,
        page_count: int | None = None,
        error_msg: str | None = None,
    ) -> Document | None:
        with self.session_factory() as session:
            row = session.get(Document, document_id)
            if not row:
                return None
            if status is not None:
                row.status = status
            if page_count is not None:
                row.page_count = page_count
            row.error_msg = error_msg
            row.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(row)
            return row

    def delete_document(self, document_id: str) -> Document | None:
        with self.session_factory() as session:
            row = session.get(Document, document_id)
            if not row:
                return None
            session.delete(row)
            session.commit()
            return row

    @staticmethod
    def remove_file(path: str) -> None:
        file_path = Path(path)
        if file_path.exists():
            file_path.unlink()

