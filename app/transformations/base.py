from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd


@dataclass
class BaseTransformation(ABC):
    name: str
    description: str = ""

    @abstractmethod
    def transform(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply the transformation to the data.

        Args:
            data: Input DataFrame to transform
            params: Dictionary of parameters for the transformation

        Returns:
            Transformed DataFrame
        """
        pass

    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Validate the parameters for this transformation.

        Args:
            params: Dictionary of parameters to validate

        Returns:
            True if parameters are valid, False otherwise
        """
        pass

    def get_info(self) -> Dict[str, str]:
        """Get information about this transformation."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
        }
