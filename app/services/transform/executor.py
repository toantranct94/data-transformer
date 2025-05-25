import io
from typing import Any, Dict

import pandas as pd

from app.exception.errors import FileError, PipelineError
from app.services.file.storage import read_file_from_upload_directory
from app.services.transform.pipeline import TransformationPipeline


class PipelineExecutor:

    @staticmethod
    async def execute_pipeline(
        filename: str, pipeline: TransformationPipeline
    ) -> Dict[str, Any]:
        """
        Execute a transformation pipeline on a file.

        Args:
            filename: Name of the file to transform
            pipeline: Pipeline to execute

        Returns:
            Dictionary containing transformation results

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If pipeline validation fails
            Exception: If transformation fails
        """
        try:
            content = await read_file_from_upload_directory(filename)
            csv_data = pd.read_csv(io.StringIO(content.decode("utf-8")))

            result_data = pipeline.execute(csv_data)
            result_json = result_data.to_dict(orient="records")

            return {
                "original_shape": csv_data.shape,
                "transformed_shape": result_data.shape,
                "pipeline_info": pipeline.get_pipeline_info(),
                "data": result_json,
            }

        except FileNotFoundError:
            raise FileError(
                message=f"File not found: {filename}", details={"filename": filename}
            )
        except Exception as e:
            raise PipelineError(
                message="Pipeline execution failed", details={"error": str(e)}
            )
