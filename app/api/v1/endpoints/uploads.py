import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile

router = APIRouter()

UPLOAD_DIR = Path("uploads/dogs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/dog-photo")
async def upload_dog_photo(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()

    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"

    filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / filename

    content = await file.read()
    file_path.write_bytes(content)

    return {
        "photo_url": f"/uploads/dogs/{filename}"
    }