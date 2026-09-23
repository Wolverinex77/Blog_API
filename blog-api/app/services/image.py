import io
import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.core import exceptions

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads" / "cover_image"

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
FORMAT_EXTENSIONS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}
MAX_FILE_SIZE = 5 * 1024 * 1024


async def save_image(image: UploadFile) -> str:
    if image.content_type not in ALLOWED_TYPES:
        raise exceptions.InvalidImageTypeError()

    contents = await image.read()
    if len(contents) > MAX_FILE_SIZE:
        raise exceptions.ImageTooLargeError()

    try:
        with Image.open(io.BytesIO(contents)) as uploaded_image:
            uploaded_image.verify()
            image_format = uploaded_image.format
    except (UnidentifiedImageError, OSError):
        raise exceptions.InvalidImageError()

    if image_format is None:
        raise exceptions.ImageFormatError()

    extension = FORMAT_EXTENSIONS.get(image_format)
    if extension is None:
        raise exceptions.ImageFormatError()

    filename = f"{uuid.uuid4()}{extension}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / filename).write_bytes(contents)

    return f"/uploads/cover_image/{filename}"
