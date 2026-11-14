"""check_schema — schemas pass the Draft 2020-12 metaschema; every
examples/*.yaml validates against schema/dispatch.schema.json.

Usage: python3 scripts/ci/check_schema.py      (from the repo root)
Needs: jsonschema, pyyaml. Exit: 0 pass, 1 any failure. Quiet on success.
"""
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

failed = False

def fail(msg):
    global failed
    failed = True
    print(msg, file=sys.stderr)

schemas = {}
for path in sorted(Path("schema").glob("*.json")):
    schema = json.loads(path.read_text(encoding="utf-8"))
    schemas[path.name] = schema
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as e:  # SchemaError
        fail(f"{path}: metaschema: {e.message if hasattr(e, 'message') else e}")

dispatch = Draft202012Validator(schemas["dispatch.schema.json"])
for path in sorted(Path("examples").glob("*.yaml")):
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    for err in sorted(dispatch.iter_errors(doc), key=lambda e: list(e.path)):
        where = "/".join(map(str, err.path)) or "<root>"
        fail(f"{path}: {where}: {err.message}")

sys.exit(1 if failed else 0)
