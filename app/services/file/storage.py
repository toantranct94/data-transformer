import os
from typing import List

import aiofiles
from fastapi import UploadFile
from loguru import logger

from app.configs.base import settings
from app.exception.errors import FileError


async def store_file(file: UploadFile, filename: str) -> None:
    """
    Store an uploaded file to disk.

    Args:
        file: The uploaded file to store
        filename: The target filename to save as

    Raises:
        Exception: If file storage fails
    """
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, filename)
    temp_path = f"{file_path}.tmp"

    try:
        os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)

        async with aiofiles.open(temp_path, "wb") as out_file:
            while content := await file.read(settings.MAX_READ_CHUNK_BYTES):
                await out_file.write(content)

        os.rename(temp_path, file_path)

    except Exception as e:
        await cleanup_temp_file(temp_path)
        raise FileError(message="Failed to store file", details={"error": str(e)})


async def read_file_from_upload_directory(filename: str) -> bytes:
    """
    Read a file from the upload directory.
    """
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, filename)
    return await read_file(file_path)


async def delete_file(filename: str) -> None:
    """
    Delete a file from the local directory.
    """
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


async def cleanup_temp_file(temp_path: str) -> None:
    """
    Clean up temporary file if it exists.

    Args:
        temp_path: Path to the temporary file
    """
    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except Exception as e:
        logger.error(f"Error cleaning up temp file {temp_path}: {str(e)}")


async def read_file(filepath: str) -> bytes:
    """
    Read file contents.

    Args:
        filename: Name of the file to read

    Returns:
        File contents as bytes

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} not found")

    async with aiofiles.open(filepath, "rb") as file:
        return await file.read()


async def get_csv_columns(filename: str) -> List[str]:
    """
    Get the column names from a CSV file without loading all content.

    Args:
        filename: Name of the CSV file to read

    Returns:
        List of column names

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {filename} not found")

    async with aiofiles.open(file_path, "r") as file:
        first_line = await file.readline()
        columns = first_line.strip().split(",")
        return columns
