"""File storage abstraction — local filesystem implementation."""

import os
import uuid
from pathlib import Path


class StorageBackend:
    """Abstract storage interface."""

    def save(self, file_bytes: bytes, user_id: int, filename: str, content_type: str) -> str:
        raise NotImplementedError

    def delete(self, stored_path: str) -> None:
        raise NotImplementedError

    def get_url(self, stored_path: str) -> str:
        raise NotImplementedError

    def get_full_path(self, stored_path: str) -> Path:
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """Store files on local filesystem."""

    def __init__(self, upload_dir: str = "uploads"):
        self.base_dir = Path(upload_dir)

    def save(self, file_bytes: bytes, user_id: int, filename: str, content_type: str) -> str:
        ext = Path(filename).suffix.lower() or ".jpg"
        stored_name = f"{uuid.uuid4().hex}{ext}"
        user_dir = self.base_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_dir / stored_name
        file_path.write_bytes(file_bytes)
        return f"{user_id}/{stored_name}"

    def delete(self, stored_path: str) -> None:
        file_path = self.base_dir / stored_path
        if file_path.exists():
            file_path.unlink()

    def get_url(self, stored_path: str) -> str:
        return f"/uploads/{stored_path}"

    def get_full_path(self, stored_path: str) -> Path:
        return self.base_dir / stored_path


_storage: StorageBackend | None = None


def get_storage() -> StorageBackend:
    global _storage
    if _storage is None:
        upload_dir = os.environ.get("UPLOAD_DIR", "uploads")
        _storage = LocalStorage(upload_dir)
    return _storage
