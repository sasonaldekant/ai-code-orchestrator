from core.output_validator import validate
import json

schema = {"type":"object", "properties":{"x":{"type":"number"}}, "required":["x"]}

def test_validate_pass():
    ok, err = validate(json.dumps({"x":1}), schema)
    assert ok and err is None

def test_validate_fail():
    ok, err = validate(json.dumps({"y":2}), schema)
    assert not ok and "Schema validation error" in err
