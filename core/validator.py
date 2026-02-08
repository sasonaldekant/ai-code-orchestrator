"""
JSON Schema validation for agent outputs.

This validator loads schemas from the `schemas/phase_schemas` directory and
ensures that outputs match the required structure.  Errors are returned
alongside a boolean flag indicating validity.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any
import jsonschema
import logging

logger = logging.getLogger(__name__)


class OutputValidator:
    """Validate dictionaries against JSON schema files."""

    def __init__(self, schemas_base: str = "schemas/phase_schemas") -> None:
        self.schemas_base = Path(schemas_base)
        self.cache: Dict[str, Dict[str, Any]] = {}

    def load_schema(self, name: str) -> Dict[str, Any]:
        """Load a JSON schema by name (without .json suffix)."""
        schema_path = self.schemas_base / f"{name}.json"
        if schema_path in self.cache:
            return self.cache[str(schema_path)]
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
                self.cache[str(schema_path)] = schema
                return schema
        except Exception as exc:
            logger.error(f"Failed to load schema {schema_path}: {exc}")
            raise

    def validate(self, data: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
        """
        Validate data against the named schema.

        Parameters
        ----------
        data: dict
            The object to validate.
        schema_name: str
            Name of the schema file (without extension) under schemas_base.

        Returns
        -------
        dict
            Contains keys: `valid` (bool) and `errors` (list of strings).
        """
        try:
            schema = self.load_schema(schema_name)
        except Exception as exc:
            return {"valid": False, "errors": [str(exc)]}
        try:
            jsonschema.validate(instance=data, schema=schema)
            return {"valid": True, "errors": []}
        except jsonschema.ValidationError as e:
            return {"valid": False, "errors": [e.message]}
