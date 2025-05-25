import uuid

from fastapi import HTTPException, UploadFile, status
from loguru import logger

from app.dtos.upload.response import UploadFileResponse
from app.services.file.storage import delete_file, store_file
from app.services.file.validation import validate_csv_file


class FileUploadService:

    async def upload_file(self, file: UploadFile) -> UploadFileResponse:
        """
        Handle file upload process including validation and storage.

        Args:
            file: The uploaded file to process

        Returns:
            UploadFileResponse containing the saved filename

        Raises:
            HTTPException: If validation fails or storage errors occur
        """
        await validate_csv_file(file)

        try:
            save_filename = f"{str(uuid.uuid4())}.csv"

            await store_file(file, save_filename)

            logger.info(f"Successfully saved file: {save_filename}")

            return UploadFileResponse(
                filename=save_filename,
                status="success",
            )

        except Exception as e:
            logger.error(f"Error saving file {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing file",
            )

    async def delete_file(self, filename: str) -> None:
        """
        Delete a file from the local directory.
        """
        return await delete_file(filename)
