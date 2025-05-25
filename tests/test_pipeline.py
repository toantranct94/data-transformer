import pandas as pd

from app.services.transform.pipeline import TransformationPipeline


def test_complete_pipeline_workflow():
    data = pd.DataFrame(
        {
            "name": ["alice", "bob", "charlie"],
            "age": [25, 30, 35],
            "status": ["active", "inactive", "active"],
        }
    )

    pipeline = TransformationPipeline(
        [
            {
                "transformation": "filter",
                "params": {"column": "age", "operator": "gt", "value": 30},
            },
            {"transformation": "uppercase", "params": {"columns": ["name"]}},
        ]
    )

    result = pipeline.execute(data)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "CHARLIE"


def test_pipeline_formats():
    json_pipeline = """
    {
        "steps": [
            {"transformation": "filter", "params": {"column": "age", "operator": "gt", "value": 30}}
        ]
    }
    """
    yaml_pipeline = """
    steps:
      - transformation: filter
        params:
          column: age
          operator: gt
          value: 30
    """

    json_result = TransformationPipeline.from_json(json_pipeline)
    yaml_result = TransformationPipeline.from_yaml(yaml_pipeline)

    assert json_result.steps == yaml_result.steps
