from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field


class TransformResponse(BaseModel):
    original_shape: Tuple[int, int] = Field(
        ..., description="Original shape of the data"
    )
    transformed_shape: Tuple[int, int] = Field(
        ..., description="Transformed shape of the data"
    )
    pipeline_info: Dict[str, Any] = Field(..., description="Pipeline information")
    data: List[Dict[str, Any]] = Field(..., description="Transformed data")


class TransformHealthCheckResponse(BaseModel):
    status: str = Field(..., description="Status of the transform")
    transformations_available: int = Field(
        ..., description="Number of transformations available"
    )
    registry_config: Dict[str, Any] = Field(..., description="Registry configuration")


class TransformValidationResponse(BaseModel):
    valid: bool = Field(..., description="Whether the pipeline is valid")
    errors: List[str] = Field(..., description="Errors in the pipeline")
    pipeline_info: Dict[str, Any] = Field(..., description="Pipeline information")


class PipelineConfigResponse(BaseModel):
    configuration: Dict[str, bool] = Field(..., description="Registry configuration")
    enabled_count: int = Field(..., description="Number of enabled transformations")


class UpdatePipelineConfigResponse(BaseModel):
    message: str = Field(..., description="Message indicating the result of the update")
    new_config: Dict[str, Any] = Field(
        ..., description="Updated registry configuration"
    )


class TransformationsResponse(BaseModel):
    transformations: List[Dict[str, Any]] = Field(
        ..., description="List of transformations"
    )
    count: int = Field(..., description="Number of transformations")
