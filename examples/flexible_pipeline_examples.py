import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.pipeline import PipelineBuilder, TransformationPipeline


def main():
    """Run examples of different pipeline definition formats."""
    data_path = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    data = pd.read_csv(data_path)

    print(f"Loaded data with shape: {data.shape}")
    print("\nOriginal data sample:")
    print(data.head(3))

    # Example 1: JSON-based pipeline definition
    print("\n\n" + "=" * 50)
    print("Example 1: JSON-based pipeline definition")

    json_pipeline = """
    {
        "steps": [
            {
                "transformation": "filter",
                "params": {
                    "column": "age",
                    "operator": "gt",
                    "value": 30
                }
            },
            {
                "transformation": "uppercase",
                "params": {
                    "columns": ["first_name"]
                }
            }
        ]
    }
    """

    pipeline = TransformationPipeline.from_json(json_pipeline)

    result = pipeline.execute(data)

    print("\nTransformed data (JSON pipeline):")
    print(result.head())

    # Example 2: YAML-based pipeline definition
    print("\n\n" + "=" * 50)
    print("Example 2: YAML-based pipeline definition")

    yaml_pipeline = """
    steps:
      - transformation: filter
        params:
          column: status
          operator: eq
          value: active
      - transformation: uppercase
        params:
          columns:
            - first_name
            - last_name
      - transformation: map_column
        params:
          type: rename
          mapping:
            first_name: firstName
            last_name: lastName
      - transformation: sort
        params:
          column: age
          ascending: false
    """

    pipeline = TransformationPipeline.from_yaml(yaml_pipeline)

    result = pipeline.execute(data)

    print("\nTransformed data (YAML pipeline):")
    print(result.head())

    # Example 3: Builder API
    print("\n\n" + "=" * 50)
    print("Example 3: Builder API")

    # Create pipeline using the fluent builder API
    pipeline = (
        PipelineBuilder()
        .filter(column="city", operator="contains", value="san")
        .uppercase(columns=["first_name", "last_name"])
        .map_column(mapping={"first_name": "firstName", "last_name": "lastName"})
        .sort(column="age", ascending=False)
        .build()
    )

    result = pipeline.execute(data)

    print("\nTransformed data (Builder API):")
    print(result.head())

    # Example 4: Save and load pipeline
    print("\n\n" + "=" * 50)
    print("Example 4: Save and load pipeline")

    # Save pipeline to JSON
    json_output = pipeline.to_json()
    json_file = os.path.join(os.path.dirname(__file__), "saved_pipeline.json")
    with open(json_file, "w") as f:
        f.write(json_output)

    print(f"Saved pipeline to {json_file}")

    yaml_output = pipeline.to_yaml()
    yaml_file = os.path.join(os.path.dirname(__file__), "saved_pipeline.yaml")
    with open(yaml_file, "w") as f:
        f.write(yaml_output)

    print(f"Saved pipeline to {yaml_file}")

    loaded_pipeline = TransformationPipeline.from_file(json_file)

    result = loaded_pipeline.execute(data)

    print("\nTransformed data (Loaded pipeline):")
    print(result.head())

    # Example 5: Direct dictionary definition
    print("\n\n" + "=" * 50)
    print("Example 5: Direct dictionary definition")

    # Define pipeline as a Python dictionary
    pipeline_dict = {
        "steps": [
            {
                "transformation": "filter",
                "params": {"column": "age", "operator": "gte", "value": 35},
            }
        ]
    }

    pipeline = TransformationPipeline.from_config(pipeline_dict)

    result = pipeline.execute(data)

    print("\nTransformed data (Dictionary pipeline):")
    print(result.head())


if __name__ == "__main__":
    main()
