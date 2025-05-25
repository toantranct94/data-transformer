from typing import Any, Dict

import pandas as pd

from app.transformations.base import BaseTransformation


class FilterTransformation(BaseTransformation):

    def __init__(self):
        super().__init__(
            name="filter", description="Filter rows based on column conditions"
        )

    def transform(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Filter rows based on conditions.

        Expected params:
        - column: column name to filter on
        - operator: one of ['eq', 'ne', 'gt', 'lt', 'gte', 'lte', 'contains']
        - value: value to compare against
        """
        column = params["column"]
        operator = params["operator"]
        value = params["value"]

        if column not in data.columns:
            raise ValueError(f"Column '{column}' not found in data")

        if operator == "eq":
            return data[data[column] == value]
        elif operator == "ne":
            return data[data[column] != value]
        elif operator == "gt":
            return data[data[column] > value]
        elif operator == "lt":
            return data[data[column] < value]
        elif operator == "gte":
            return data[data[column] >= value]
        elif operator == "lte":
            return data[data[column] <= value]
        elif operator == "contains":
            return data[data[column].astype(str).str.contains(str(value), na=False)]
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def validate_params(self, params: Dict[str, Any]) -> bool:
        required_keys = ["column", "operator", "value"]
        valid_operators = ["eq", "ne", "gt", "lt", "gte", "lte", "contains"]

        return (
            all(key in params for key in required_keys)
            and params["operator"] in valid_operators
        )


class MapColumnTransformation(BaseTransformation):
    """Map/rename columns or apply value mappings."""

    def __init__(self):
        super().__init__(
            name="map_column", description="Rename columns or map column values"
        )

    def transform(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Map/rename columns or values.

        Expected params:
        - type: 'rename' or 'value_map'
        - mapping: dictionary of old->new mappings
        - column: (for value_map) column to apply value mapping to
        """
        result = data.copy()
        map_type = params["type"]
        mapping = params["mapping"]

        if map_type == "rename":
            result = result.rename(columns=mapping)
        elif map_type == "value_map":
            column = params["column"]
            if column not in result.columns:
                raise ValueError(f"Column '{column}' not found in data")
            result[column] = result[column].map(mapping).fillna(result[column])
        else:
            raise ValueError(f"Unsupported map type: {map_type}")

        return result

    def validate_params(self, params: Dict[str, Any]) -> bool:
        if "type" not in params or "mapping" not in params:
            return False

        map_type = params["type"]
        if map_type not in ["rename", "value_map"]:
            return False

        if map_type == "value_map" and "column" not in params:
            return False

        return isinstance(params["mapping"], dict)


class UppercaseTransformation(BaseTransformation):

    def __init__(self):
        super().__init__(
            name="uppercase", description="Convert string columns to uppercase"
        )

    def transform(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert specified columns to uppercase.

        Expected params:
        - columns: list of column names to convert (or 'all' for all string columns)
        """
        result = data.copy()
        columns = params.get("columns", "all")

        if columns == "all":
            # Apply to all string/object columns
            string_columns = result.select_dtypes(include=["object"]).columns
            for col in string_columns:
                result[col] = result[col].astype(str).str.upper()
        else:
            # Apply to specified columns
            for col in columns:
                if col not in result.columns:
                    raise ValueError(f"Column '{col}' not found in data")
                result[col] = result[col].astype(str).str.upper()

        return result

    def validate_params(self, params: Dict[str, Any]) -> bool:
        if "columns" not in params:
            return False

        columns = params["columns"]
        return columns == "all" or isinstance(columns, list)


class SortTransformation(BaseTransformation):

    def __init__(self):
        super().__init__(
            name="sort", description="Sort rows based on column conditions"
        )

    def transform(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Sort rows based on conditions.

        Expected params:
        - column: column name to sort on
        - ascending: boolean indicating ascending or descending order
        """
        column = params["column"]
        ascending = params["ascending"]

        return data.sort_values(by=column, ascending=ascending)

    def validate_params(self, params: Dict[str, Any]) -> bool:
        if "column" not in params:
            return False

        return isinstance(params["ascending"], bool)
