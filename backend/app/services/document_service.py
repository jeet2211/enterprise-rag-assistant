from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from app.models.db import Document


class DocumentService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create_document(
        self,
        *,
        document_id: str,
        filename: str,
        file_path: str,
        file_size: int,
        file_hash: str | None = None,
    ) -> Document:
        with self.session_factory() as session:
            row = Document(
                id=document_id,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                file_hash=file_hash,
                status="uploaded",
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

    def get_by_hash(self, file_hash: str) -> Document | None:
        """Look up an existing document by its SHA-256 file hash (for deduplication)."""
        with self.session_factory() as session:
            stmt = select(Document).where(Document.file_hash == file_hash)
            return session.scalars(stmt).first()

    def update_document(
        self,
        document_id: str,
        *,
        status: str | None = None,
        page_count: int | None = None,
        chunk_count: int | None = None,
        error_msg: str | None = None,
        file_hash: str | None = None,
    ) -> Document | None:
        with self.session_factory() as session:
            row = session.get(Document, document_id)
            if not row:
                return None
            if status is not None:
                row.status = status
            if page_count is not None:
                row.page_count = page_count
            if chunk_count is not None:
                row.chunk_count = chunk_count
            if file_hash is not None:
                row.file_hash = file_hash
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

    def get_stats(self) -> dict[str, int]:
        """Return aggregate counts for the health endpoint."""
        with self.session_factory() as session:
            docs = list(session.scalars(select(Document)).all())
        total = len(docs)
        ready = sum(1 for d in docs if d.status == "ready")
        failed = sum(1 for d in docs if d.status == "failed")
        processing = total - ready - failed
        return {"total": total, "ready": ready, "failed": failed, "processing": processing}

    @staticmethod
    def remove_file(path: str) -> None:
        file_path = Path(path)
        if file_path.exists():
            file_path.unlink()
