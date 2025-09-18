import json, jsonschema

def validate(output_str: str, schema: dict) -> tuple[bool, str | None]:
    try:
        data = json.loads(output_str)
        jsonschema.validate(instance=data, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, f"Schema validation error: {e.message}"
    except Exception as e:
        return False, f"Invalid JSON: {e}"
