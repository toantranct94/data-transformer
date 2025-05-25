from typing import Any, Dict, List

from pydantic import BaseModel, Field


class RegistryConfig(BaseModel):
    config: Dict[str, bool] = Field(..., description="Registry configuration")


class PipelineConfig(BaseModel):
    steps: List[Dict[str, Any]] = Field(..., description="Pipeline configuration")


class BaseTransformRequest(BaseModel):
    filename: str = Field(..., description="Filename of the file to transform")


class TransformFromJsonRequest(BaseTransformRequest):
    pipeline: PipelineConfig = Field(..., description="Pipeline configuration")


class TransformFromYamlRequest(BaseTransformRequest):
    pipeline: str = Field(..., description="YAML pipeline configuration")


class AiGeneratePipelineRequest(BaseTransformRequest):
    prompt: str = Field(..., description="Prompt to generate a pipeline")
