from typing import Dict, List, Optional

from app.transformations.base import BaseTransformation
from app.transformations.implementations import (
    FilterTransformation,
    MapColumnTransformation,
    SortTransformation,
    UppercaseTransformation,
)


class TransformationRegistry:

    def __init__(self):
        self._transformations: Dict[str, BaseTransformation] = {}
        self._enabled_transformations: Dict[str, bool] = {}
        self._initialize_default_transformations()

    def _initialize_default_transformations(self):
        default_transformations = [
            FilterTransformation(),
            MapColumnTransformation(),
            SortTransformation(),
            UppercaseTransformation(),
        ]

        for transformation in default_transformations:
            self.register(transformation, enabled=True)

    def register(
        self,
        transformation: BaseTransformation,
        enabled: bool = True,
        alias: Optional[str] = None,
    ):
        """
        Register a transformation in the registry.

        Args:
            transformation: The transformation instance to register
            enabled: Whether the transformation is enabled by default
            alias: Optional alias name for the transformation
        """
        name = alias or transformation.name
        self._transformations[name] = transformation
        self._enabled_transformations[name] = enabled

    def unregister(self, name: str):
        if name in self._transformations:
            del self._transformations[name]
            del self._enabled_transformations[name]

    def enable(self, name: str):
        if name in self._transformations:
            self._enabled_transformations[name] = True
        else:
            raise ValueError(f"Transformation '{name}' not found in registry")

    def disable(self, name: str):
        if name in self._transformations:
            self._enabled_transformations[name] = False
        else:
            raise ValueError(f"Transformation '{name}' not found in registry")

    def is_enabled(self, name: str) -> bool:
        return self._enabled_transformations.get(name, False)

    def get_transformation(self, name: str) -> Optional[BaseTransformation]:
        if name in self._transformations and self.is_enabled(name):
            return self._transformations[name]
        return None

    def list_available(self, enabled_only: bool = True) -> List[Dict[str, str]]:
        result = []
        for name, transformation in self._transformations.items():
            if not enabled_only or self.is_enabled(name):
                info = transformation.get_info()
                info["alias"] = name
                info["enabled"] = self.is_enabled(name)
                result.append(info)
        return result

    def get_configuration(self) -> Dict[str, bool]:
        return self._enabled_transformations.copy()

    def set_configuration(self, config: Dict[str, bool]):
        for name, enabled in config.items():
            if name in self._transformations:
                self._enabled_transformations[name] = enabled
