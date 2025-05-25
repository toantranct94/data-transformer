import pandas as pd
import pytest

from app.services.registry import TransformationRegistry
from app.services.transform.pipeline import TransformationPipeline
from app.transformations.implementations import (
    FilterTransformation,
    MapColumnTransformation,
    SortTransformation,
    UppercaseTransformation,
)


class TestFilterTransformation:
    def setup_method(self):
        self.filter_transform = FilterTransformation()
        self.test_data = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie", "Diana"],
                "age": [25, 30, 35, 28],
                "city": ["New York", "London", "Paris", "Tokyo"],
            }
        )

    def test_filter_equal(self):
        params = {"column": "age", "operator": "eq", "value": 30}
        result = self.filter_transform.transform(self.test_data, params)
        assert len(result) == 1
        assert result.iloc[0]["name"] == "Bob"

    def test_filter_greater_than(self):
        params = {"column": "age", "operator": "gt", "value": 28}
        result = self.filter_transform.transform(self.test_data, params)
        assert len(result) == 2
        assert "Bob" in result["name"].values
        assert "Charlie" in result["name"].values

    def test_filter_contains(self):
        params = {"column": "city", "operator": "contains", "value": "on"}
        result = self.filter_transform.transform(self.test_data, params)
        assert len(result) == 1
        assert result.iloc[0]["city"] == "London"

    def test_validate_params(self):
        valid_params = {"column": "age", "operator": "eq", "value": 30}
        assert self.filter_transform.validate_params(valid_params)

        invalid_params = {"column": "age", "operator": "invalid", "value": 30}
        assert not self.filter_transform.validate_params(invalid_params)


class TestMapColumnTransformation:
    def setup_method(self):
        self.map_transform = MapColumnTransformation()
        self.test_data = pd.DataFrame(
            {"first_name": ["Alice", "Bob"], "status": ["active", "inactive"]}
        )

    def test_rename_columns(self):
        params = {"type": "rename", "mapping": {"first_name": "name"}}
        result = self.map_transform.transform(self.test_data, params)
        assert "name" in result.columns
        assert "first_name" not in result.columns

    def test_value_mapping(self):
        params = {
            "type": "value_map",
            "column": "status",
            "mapping": {"active": 1, "inactive": 0},
        }
        result = self.map_transform.transform(self.test_data, params)
        assert result["status"].tolist() == [1, 0]

    def test_validate_params(self):
        valid_params = {"type": "rename", "mapping": {"old": "new"}}
        assert self.map_transform.validate_params(valid_params)

        invalid_params = {"type": "invalid"}
        assert not self.map_transform.validate_params(invalid_params)


class TestUppercaseTransformation:
    def setup_method(self):
        self.uppercase_transform = UppercaseTransformation()
        self.test_data = pd.DataFrame(
            {"name": ["alice", "bob"], "city": ["new york", "london"], "age": [25, 30]}
        )

    def test_uppercase_all_strings(self):
        params = {"columns": "all"}
        result = self.uppercase_transform.transform(self.test_data, params)
        assert result["name"].tolist() == ["ALICE", "BOB"]
        assert result["city"].tolist() == ["NEW YORK", "LONDON"]
        assert result["age"].tolist() == [25, 30]

    def test_uppercase_specific_columns(self):
        params = {"columns": ["name"]}
        result = self.uppercase_transform.transform(self.test_data, params)
        assert result["name"].tolist() == ["ALICE", "BOB"]
        assert result["city"].tolist() == ["new york", "london"]  # unchanged

    def test_validate_params(self):
        valid_params = {"columns": ["name"]}
        assert self.uppercase_transform.validate_params(valid_params)

        valid_params_all = {"columns": "all"}
        assert self.uppercase_transform.validate_params(valid_params_all)

        invalid_params = {}
        assert not self.uppercase_transform.validate_params(invalid_params)


class TestTransformationRegistry:
    def setup_method(self):
        self.registry = TransformationRegistry()

    def test_default_transformations_loaded(self):
        transformations = self.registry.list_available()
        assert len(transformations) == 4

        names = [t["alias"] for t in transformations]
        assert "filter" in names
        assert "map_column" in names
        assert "uppercase" in names

    def test_enable_disable_transformations(self):
        self.registry.disable("filter")
        assert not self.registry.is_enabled("filter")

        transformations = self.registry.list_available(enabled_only=True)
        names = [t["alias"] for t in transformations]
        assert "filter" not in names

        self.registry.enable("filter")
        assert self.registry.is_enabled("filter")

    def test_get_transformation(self):
        transformation = self.registry.get_transformation("filter")
        assert transformation is not None
        assert isinstance(transformation, FilterTransformation)

        self.registry.disable("filter")
        transformation = self.registry.get_transformation("filter")
        assert transformation is None


class TestTransformationPipeline:
    def setup_method(self):
        self.test_data = pd.DataFrame(
            {
                "name": ["alice", "bob", "charlie"],
                "age": [25, 30, 35],
                "status": ["active", "inactive", "active"],
            }
        )

    def test_simple_pipeline(self):
        steps = [
            {
                "transformation": "filter",
                "params": {"column": "age", "operator": "gte", "value": 30},
            },
            {"transformation": "uppercase", "params": {"columns": ["name"]}},
        ]

        pipeline = TransformationPipeline(steps)
        result = pipeline.execute(self.test_data)

        # Should have 2 rows (age >= 30) with uppercase names
        assert len(result) == 2
        assert result["name"].tolist() == ["BOB", "CHARLIE"]

    def test_complex_pipeline(self):
        steps = [
            {
                "transformation": "map_column",
                "params": {
                    "type": "value_map",
                    "column": "status",
                    "mapping": {"active": 1, "inactive": 0},
                },
            },
            {
                "transformation": "filter",
                "params": {"column": "status", "operator": "eq", "value": 1},
            },
            {
                "transformation": "map_column",
                "params": {"type": "rename", "mapping": {"name": "full_name"}},
            },
        ]

        pipeline = TransformationPipeline(steps)
        result = pipeline.execute(self.test_data)

        # Should have 2 rows (active status = 1) with renamed column
        assert len(result) == 2
        assert "full_name" in result.columns
        assert "name" not in result.columns
        assert result["status"].tolist() == [1, 1]

    def test_pipeline_validation(self):
        # Valid pipeline
        valid_steps = [
            {
                "transformation": "filter",
                "params": {"column": "age", "operator": "eq", "value": 30},
            }
        ]
        pipeline = TransformationPipeline(valid_steps)
        errors = pipeline.validate_pipeline()
        assert len(errors) == 0

        # Invalid pipeline - missing transformation
        invalid_steps = [{"params": {"column": "age", "operator": "eq", "value": 30}}]
        pipeline = TransformationPipeline(invalid_steps)
        errors = pipeline.validate_pipeline()
        assert len(errors) > 0

        # Invalid pipeline - unknown transformation
        invalid_steps = [
            {
                "transformation": "unknown",
                "params": {"column": "age", "operator": "eq", "value": 30},
            }
        ]
        pipeline = TransformationPipeline(invalid_steps)
        errors = pipeline.validate_pipeline()
        assert len(errors) > 0

    def test_pipeline_from_config(self):
        config = {
            "steps": [{"transformation": "uppercase", "params": {"columns": "all"}}]
        }

        pipeline = TransformationPipeline.from_config(config)
        assert len(pipeline.steps) == 1
        assert pipeline.steps[0]["transformation"] == "uppercase"


class TestSortTransformation:
    def setup_method(self):
        self.sort_transform = SortTransformation()
        self.test_data = pd.DataFrame(
            {"name": ["alice", "bob", "charlie"], "age": [25, 30, 35]}
        )

    def test_sort_ascending(self):
        params = {"column": "age", "ascending": True}
        result = self.sort_transform.transform(self.test_data, params)
        assert result["name"].tolist() == ["alice", "bob", "charlie"]

    def test_sort_descending(self):
        params = {"column": "age", "ascending": False}
        result = self.sort_transform.transform(self.test_data, params)
        assert result["name"].tolist() == ["charlie", "bob", "alice"]


if __name__ == "__main__":
    pytest.main([__file__])
