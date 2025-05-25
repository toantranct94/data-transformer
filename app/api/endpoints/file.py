from fastapi import APIRouter, File, UploadFile

from app.services.file import upload_service

router = APIRouter()


@router.post("/upload")
async def store_file(file: UploadFile = File(...)):
    """
    Store CSV file in a local directory with a unique ID as the filename.

    Args:
        file: CSV file to store
    """
    return await upload_service.upload_file(file)


@router.delete("/{filename}")
async def delete_file(filename: str):
    """
    Delete a file from the local directory.
    """
    return await upload_service.delete_file(filename)
