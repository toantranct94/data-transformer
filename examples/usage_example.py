import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.dependencies.di_container import registry
from app.services.pipeline import TransformationPipeline


def main():
    """Run example transformations on sample data."""
    # Load sample data
    data_path = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    data = pd.read_csv(data_path)

    print(f"Loaded data with shape: {data.shape}")
    print("\nOriginal data sample:")
    print(data.head(3))

    # Load example pipelines
    pipelines_path = os.path.join(os.path.dirname(__file__), "pipeline_examples.json")
    with open(pipelines_path, "r") as f:
        examples = json.load(f)["examples"]

    # List available transformations
    print("\nAvailable transformations:")
    for t in registry.list_available():
        print(f"- {t['name']}: {t['description']} (enabled: {t['enabled']})")

    # Run each example pipeline
    for example in examples:
        print(f"\n\n{'=' * 50}")
        print(f"Running example: {example['name']}")
        print(f"Description: {example['description']}")

        # Create pipeline
        pipeline = TransformationPipeline.from_config(example["pipeline"])

        # Validate pipeline
        errors = pipeline.validate_pipeline()
        if errors:
            print(f"Pipeline validation failed: {errors}")
            continue

        # Execute pipeline
        try:
            result = pipeline.execute(data)

            print(f"\nTransformed data shape: {result.shape}")
            print("\nTransformed data sample:")
            print(result.head(3))

            # Show pipeline info
            print("\nPipeline steps:")
            for i, step in enumerate(pipeline.steps):
                print(f"  {i+1}. {step['transformation']}: {step['params']}")

        except Exception as e:
            print(f"Error executing pipeline: {e}")

    # Example of programmatically creating a pipeline
    print(f"\n\n{'=' * 50}")
    print("Creating a custom pipeline programmatically")

    custom_pipeline = TransformationPipeline()

    # Add steps
    custom_pipeline.add_step(
        transformation_name="filter",
        params={"column": "city", "operator": "contains", "value": "san"},
    )

    custom_pipeline.add_step(transformation_name="uppercase", params={"columns": "all"})

    # Execute custom pipeline
    try:
        result = custom_pipeline.execute(data)

        print(f"\nTransformed data shape: {result.shape}")
        print("\nTransformed data sample:")
        print(result.head(3))

    except Exception as e:
        print(f"Error executing custom pipeline: {e}")


if __name__ == "__main__":
    main()
