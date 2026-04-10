import os
import tempfile
from pathlib import Path
from app.services.storage import LocalStorage


def test_local_storage_save_and_delete():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(tmpdir)
        stored_path = storage.save(b"fake image data", 1, "test.jpg", "image/jpeg")
        assert stored_path.startswith("1/")
        assert stored_path.endswith(".jpg")

        full_path = storage.get_full_path(stored_path)
        assert full_path.exists()
        assert full_path.read_bytes() == b"fake image data"

        url = storage.get_url(stored_path)
        assert url.startswith("/uploads/")

        storage.delete(stored_path)
        assert not full_path.exists()


def test_local_storage_creates_user_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(tmpdir)
        stored_path = storage.save(b"data", 42, "photo.png", "image/png")
        assert (Path(tmpdir) / "42").is_dir()
        storage.delete(stored_path)


def test_local_storage_unique_filenames():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(tmpdir)
        path1 = storage.save(b"a", 1, "same.jpg", "image/jpeg")
        path2 = storage.save(b"b", 1, "same.jpg", "image/jpeg")
        assert path1 != path2
        storage.delete(path1)
        storage.delete(path2)


def test_local_storage_delete_nonexistent():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(tmpdir)
        storage.delete("nonexistent/file.jpg")  # should not raise
