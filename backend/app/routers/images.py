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

    storage = get_storage()
    stored_path = storage.save(file_bytes, current_user.id, file.filename or "image.jpg", file.content_type)
    url = storage.get_url(stored_path)

    image = UploadedImage(
        user_id=current_user.id,
        original_filename=file.filename or "image.jpg",
        stored_path=stored_path,
        file_size=len(file_bytes),
        content_type=file.content_type,
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)

    # Build full URL from request
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", request.url.hostname)
    full_url = f"{scheme}://{host}{url}"

    return {"id": image.id, "url": full_url, "filename": image.original_filename}


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
