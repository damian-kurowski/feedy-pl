"""Image upload and serving endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.uploaded_image import UploadedImage
from app.models.user import User
from app.services.storage import get_storage

router = APIRouter(tags=["images"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
OPTIMIZE_THRESHOLD = 300 * 1024   # optimize if > 300KB
MAX_DIMENSION = 1200              # resize max edge to 1200px


def _optimize_image(file_bytes: bytes, content_type: str) -> tuple[bytes, str, str]:
    """Optimize an image: resize + convert to WebP if larger than threshold.

    Returns (new_bytes, new_content_type, new_extension).
    Falls back to original on any error.
    """
    if len(file_bytes) <= OPTIMIZE_THRESHOLD:
        return file_bytes, content_type, ""
    try:
        from io import BytesIO
        from PIL import Image
        img = Image.open(BytesIO(file_bytes))
        img.load()
        # Resize if needed (keep aspect ratio)
        w, h = img.size
        if max(w, h) > MAX_DIMENSION:
            img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
        # Convert to RGB if it has alpha and we want JPEG; for WebP keep alpha
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA") if img.mode != "P" else img.convert("RGBA")
        out = BytesIO()
        img.save(out, format="WEBP", quality=82, method=6)
        new_bytes = out.getvalue()
        if len(new_bytes) >= len(file_bytes):
            return file_bytes, content_type, ""
        return new_bytes, "image/webp", ".webp"
    except Exception:
        return file_bytes, content_type, ""


@router.post("/api/images/upload")
async def upload_image(
    request: Request,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Niedozwolony typ pliku: {file.content_type}. Dozwolone: JPEG, PNG, WebP",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plik za duzy. Maksymalny rozmiar: 5MB",
        )

    original_size = len(file_bytes)
    optimized_bytes, optimized_type, new_ext = _optimize_image(file_bytes, file.content_type)
    optimized_filename = file.filename or "image.jpg"
    if new_ext:
        # Replace extension
        base = optimized_filename.rsplit(".", 1)[0] if "." in optimized_filename else optimized_filename
        optimized_filename = f"{base}{new_ext}"

    storage = get_storage()
    stored_path = storage.save(optimized_bytes, current_user.id, optimized_filename, optimized_type)
    url = storage.get_url(stored_path)

    image = UploadedImage(
        user_id=current_user.id,
        original_filename=file.filename or "image.jpg",
        stored_path=stored_path,
        file_size=len(optimized_bytes),
        content_type=optimized_type,
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)

    # Build full URL from request
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", request.url.hostname)
    full_url = f"{scheme}://{host}{url}"

    return {
        "id": image.id,
        "url": full_url,
        "filename": image.original_filename,
        "original_size": original_size,
        "optimized_size": len(optimized_bytes),
        "optimized": new_ext != "",
    }


@router.delete("/api/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UploadedImage).where(
            UploadedImage.id == image_id,
            UploadedImage.user_id == current_user.id,
        )
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    storage = get_storage()
    storage.delete(image.stored_path)
    await db.delete(image)
    await db.commit()


@router.get("/uploads/{path:path}")
async def serve_upload(path: str):
    storage = get_storage()
    full_path = storage.get_full_path(path)
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path)
