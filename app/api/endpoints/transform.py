from fastapi import APIRouter, HTTPException
from loguru import logger

from app.dtos.transform.request import (
    AiGeneratePipelineRequest,
    PipelineConfig,
    RegistryConfig,
    TransformFromJsonRequest,
    TransformFromYamlRequest,
)
from app.dtos.transform.response import (
    PipelineConfigResponse,
    TransformationsResponse,
    TransformHealthCheckResponse,
    TransformResponse,
    TransformValidationResponse,
    UpdatePipelineConfigResponse,
)
from app.services import registry
from app.services.transform import pipeline_executor
from app.services.transform.pipeline import TransformationPipeline

router = APIRouter()


@router.get(
    "",
    response_model=TransformationsResponse,
)
async def list_transformations():
    """
    List all transformations.
    """
    try:
        transformations = registry.list_available()
        return TransformationsResponse(
            transformations=transformations, count=len(transformations)
        )
    except Exception as e:
        logger.error(f"Error listing transformations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/status",
    response_model=TransformHealthCheckResponse,
)
async def status():
    return TransformHealthCheckResponse(
        status="healthy",
        transformations_available=len(registry.list_available()),
        registry_config=registry.get_configuration(),
    )


@router.get(
    "/registry/config",
    response_model=PipelineConfigResponse,
)
async def get_registry_config():
    """
    Get the registry configuration.
    """
    try:
        config = registry.get_configuration()
        return PipelineConfigResponse(
            configuration=config, enabled_count=sum(config.values())
        )
    except Exception as e:
        logger.error(f"Error getting registry config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/registry/config",
    response_model=UpdatePipelineConfigResponse,
)
async def update_registry_config(config: RegistryConfig):
    """
    Update the registry configuration.

    Args:
        config: Registry configuration in request body
    """
    try:
        registry.set_configuration(config.config)
        return UpdatePipelineConfigResponse(
            message="Registry configuration updated successfully",
            new_config=registry.get_configuration(),
        )
    except Exception as e:
        logger.error(f"Error updating registry config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/pipeline/examples",
)
async def get_pipeline_examples():
    """
    Get examples of pipelines.
    """
    return await TransformationPipeline.get_pipeline_examples()


@router.post(
    "/pipeline/generate-from-ai",
)
async def ai_generate_pipeline(request: AiGeneratePipelineRequest):
    """
    Generate a pipeline from AI.

    Args:
        filename: CSV file to generate a pipeline from
        prompt: Prompt to generate a pipeline
    """
    try:
        return await TransformationPipeline.from_ai_generated(
            request.filename, request.prompt
        )

    except Exception as e:
        logger.error(f"Error transforming data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/execute/json",
    response_model=TransformResponse,
)
async def transform_data_json(request: TransformFromJsonRequest):
    """
    Transform CSV data using a pipeline defined in the request body as JSON.

    Args:
        filename: CSV file to transform
        pipeline: Pipeline configuration in request body
    """
    try:
        pipeline = TransformationPipeline.from_config(request.pipeline.model_dump())
        return await pipeline_executor.execute_pipeline(request.filename, pipeline)
    except Exception as e:
        logger.error(f"Error transforming data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/execute/yaml",
    response_model=TransformResponse,
)
async def transform_data_yaml(request: TransformFromYamlRequest):
    """
    Transform CSV data using a pipeline defined in YAML format.

    Args:
        filename: CSV file to transform
        pipeline: YAML string of pipeline configuration
    """
    try:
        try:
            pipeline = TransformationPipeline.from_yaml(request.pipeline)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid YAML pipeline configuration: {str(e)}"
            )

        return await pipeline_executor.execute_pipeline(request.filename, pipeline)

    except Exception as e:
        logger.error(f"Error transforming data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/validate",
    response_model=TransformValidationResponse,
)
async def validate_pipeline(pipeline_config: PipelineConfig):
    """
    Validate a pipeline configuration without executing it.

    Args:
        pipeline_config: Pipeline configuration in request body
    """
    try:
        pipeline = TransformationPipeline(pipeline_config.steps)
        validation_errors = pipeline.validate_pipeline()

        return TransformValidationResponse(
            valid=len(validation_errors) == 0,
            errors=validation_errors,
            pipeline_info=pipeline.get_pipeline_info(),
        )

    except Exception as e:
        logger.error(f"Error validating pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))
