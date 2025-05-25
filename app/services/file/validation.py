import mimetypes
import os
from typing import List

from fastapi import UploadFile

from app.configs.base import settings
from app.exception.errors import ValidationError


async def validate_csv_file(file: UploadFile) -> List[str]:
    """
    Validate uploaded CSV file.

    Args:
        file: The uploaded file to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_FILE_EXTENSIONS:
        errors.append(
            f"Invalid file extension. Allowed: {settings.ALLOWED_FILE_EXTENSIONS}"
        )

    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type != "text/csv":
        errors.append("File must be a valid CSV file")

    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    if file_size > settings.MAX_FILE_SIZE:
        errors.append("File size exceeds maximum limit")
    file.file.seek(0)

    if errors:
        raise ValidationError(
            message="File validation failed", details={"errors": errors}
        )
