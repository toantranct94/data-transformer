import json
from typing import Any, Dict, List

import pandas as pd
import yaml
from loguru import logger

from app.adapters import groq_ai_adapter
from app.services import registry
from app.services.file.storage import get_csv_columns, read_file
from app.services.transform.prompts import (
    ai_generate_pipeline_prompt,
    user_prompt_to_generate_pipeline,
)


class TransformationPipeline:
    def __init__(self, steps: List[Dict[str, Any]] = None):
        self.steps = steps or []

    def add_step(self, transformation_name: str, params: Dict[str, Any]):
        step = {"transformation": transformation_name, "params": params}
        self.steps.append(step)
        return self

    def clear_steps(self):
        self.steps.clear()
        return self

    def validate_pipeline(self) -> List[str]:
        """
        Validate the entire pipeline.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        for i, step in enumerate(self.steps):
            transformation_name = step.get("transformation")
            if not transformation_name:
                errors.append(f"Step {i}: Missing transformation name")
                continue

            transformation = registry.get_transformation(transformation_name)
            if not transformation:
                errors.append(
                    f"Step {i}: Transformation '{transformation_name}' "
                    f"not found or not enabled"
                )
                continue

            params = step.get("params", {})
            if not transformation.validate_params(params):
                errors.append(
                    f"Step {i}: Invalid parameters for "
                    f"transformation '{transformation_name}'"
                )

        return errors

    def execute(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Execute the pipeline on the provided data.

        Args:
            data: Input DataFrame

        Returns:
            Transformed DataFrame

        Raises:
            ValueError: If pipeline validation fails
            Exception: If any transformation step fails
        """
        validation_errors = self.validate_pipeline()
        if validation_errors:
            raise ValueError(f"Pipeline validation failed: {validation_errors}")

        result = data.copy()

        for i, step in enumerate(self.steps):
            try:
                transformation_name = step["transformation"]
                params = step.get("params", {})

                transformation = registry.get_transformation(transformation_name)

                logger.info(
                    f"Executing step {i + 1}/{len(self.steps)}: "
                    f"{transformation_name}"
                )

                result = transformation.transform(result, params)

                logger.info(f"Step {i + 1} completed. " f"Data shape: {result.shape}")

            except Exception as e:
                error_msg = (
                    f"Error in step {i + 1} " f"({transformation_name}): {str(e)}"
                )
                logger.error(error_msg)
                raise Exception(error_msg) from e

        return result

    def get_pipeline_info(self) -> Dict[str, Any]:
        return {
            "steps": self.steps,
            "step_count": len(self.steps),
            "validation_errors": self.validate_pipeline(),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {"steps": self.steps}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_yaml(self) -> str:
        """Convert pipeline to YAML string."""
        return yaml.dump(self.to_dict())

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "TransformationPipeline":
        """Create pipeline from configuration dictionary."""
        steps = config.get("steps", [])
        return cls(steps)

    @classmethod
    def from_json(cls, json_str: str) -> "TransformationPipeline":
        """Create pipeline from JSON string."""
        config = json.loads(json_str)
        return cls.from_config(config)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "TransformationPipeline":
        """Create pipeline from YAML string."""
        config = yaml.safe_load(yaml_str)
        return cls.from_config(config)

    @classmethod
    async def from_file(cls, file_path: str) -> "TransformationPipeline":
        """Create pipeline from configuration file."""
        with open(file_path, "r") as f:
            content = f.read()

        if file_path.endswith(".json"):
            return cls.from_json(content)
        elif file_path.endswith((".yml", ".yaml")):
            return cls.from_yaml(content)
        else:
            raise ValueError("Unsupported file format. Use .json, .yml, or .yaml")

    @classmethod
    async def from_ai_generated(
        cls, filename: str, prompt: str
    ) -> "TransformationPipeline":
        """
        Create a pipeline from an AI-generated prompt.

        Args:
            filename: Path to the input file
            prompt: User's natural language prompt describing the desired
                   transformations

        Returns:
            TransformationPipeline instance
        """
        column_info = await get_csv_columns(filename)
        messages = [
            {
                "role": "system",
                "content": ai_generate_pipeline_prompt,
            },
            {
                "role": "user",
                "content": user_prompt_to_generate_pipeline.format(
                    column_info=column_info, prompt=prompt
                ),
            },
        ]
        response = await groq_ai_adapter.async_chat_completion(
            messages, force_json_output=True
        )
        if response.get("error"):
            raise ValueError(response.get("message"))
        pipeline = cls.from_config(response)
        return pipeline

    @staticmethod
    async def get_pipeline_examples() -> List[Dict[str, Any]]:
        """
        Get examples of pipelines.
        """
        examples = await read_file("./examples/pipeline_examples.json")
        return json.loads(examples)
