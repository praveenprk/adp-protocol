"""check_conformance — conformance/ vectors follow ADP-0 §5.6, cover every
validation-table rule, and get their expected verdict from the published
schemas (ADP-A-003 C3).

Checks:
  - shape (§5.6.1, §5.6.2): path, file name, required fields, `expect`
    matching the file name, a `fail` vector listing exactly one rule;
  - coverage (§5.6.3 rule 4): every rule row in the target document's
    tables has a `pass` and a `fail` vector;
  - verdict: for a document with a published schema, the schema verdict
    equals `expect`, unless `known_defect` names an OPEN defect;
  - stale markers (§5.6.4).

Usage: python3 scripts/ci/check_conformance.py      (from the repo root)
Needs: jsonschema. Exit: 0 pass, 1 any failure. Quiet on success.
"""
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

FIELDS = ("adp_conformance", "target", "rules", "expect", "description", "input")
NAME = re.compile(r"^(pass|fail)-[a-z0-9]+(?:-[a-z0-9]+)*\.json$")
DEFECT = re.compile(r"^ADP-D-[0-9]{3}$")
RULE_ROW = re.compile(r"^\| ([A-Z]+-[0-9]{2}) +\|", re.M)
SCHEMAS = {  # doc -> kind -> schema file
    "ADP-1": {"dispatch": "schema/dispatch.schema.json",
              "report": "schema/report.schema.json"},
}

failed = False

def fail(msg):
    global failed
    failed = True
    print(msg, file=sys.stderr)

def defect_status():
    status, cur = {}, None
    for line in Path("DEFECTS.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^### (ADP-D-[0-9]{3})\s*$", line)
        if m:
            cur = m.group(1)
        elif cur and line.startswith("Status"):
            status[cur] = line.split(":", 1)[1].strip()
            cur = None
    return status

validators = {}
def verdict(doc, kind, inp):
    path = SCHEMAS.get(doc, {}).get(kind)
    if path is None:
        return None
    if path not in validators:
        validators[path] = Draft202012Validator(
            json.loads(Path(path).read_text(encoding="utf-8")))
    return "pass" if validators[path].is_valid(inp) else "fail"

status = defect_status()
covered = {}  # doc -> {"pass": set(rules), "fail": set(rules)}

root = Path("conformance")
if not root.is_dir():
    fail("conformance/: missing (ADP-0 §5.5)")
    sys.exit(1)

for path in sorted(root.rglob("*")):
    if path.is_dir():
        continue
    rel = path.relative_to(root)
    if len(rel.parts) != 3:
        fail(f"{path}: not at conformance/<doc>/<rule>/<file> (§5.6.1)")
        continue
    docdir, ruledir, name = rel.parts
    if not NAME.match(name):
        fail(f"{path}: file name is not <pass|fail>-<slug>.json (§5.6.1)")
        continue
    try:
        v = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        fail(f"{path}: not UTF-8 JSON: {e}")
        continue
    if not isinstance(v, dict):
        fail(f"{path}: not a JSON object")
        continue
    missing = [f for f in FIELDS if f not in v]
    if missing:
        fail(f"{path}: missing {', '.join(missing)} (§5.6.2)")
        continue

    t, rules, expect = v["target"], v["rules"], v["expect"]
    ok = True
    if v["adp_conformance"] != "1":
        fail(f"{path}: adp_conformance is not \"1\""); ok = False
    if not (isinstance(t, dict) and all(isinstance(t.get(k), str) and t[k] for k in ("doc", "since", "kind"))):
        fail(f"{path}: target needs doc, since, kind"); ok = False
    elif t["doc"].lower() != docdir:
        fail(f"{path}: target.doc {t['doc']} does not match directory {docdir}"); ok = False
    if not (isinstance(rules, list) and rules and all(isinstance(r, str) and r for r in rules)):
        fail(f"{path}: rules must be a non-empty list of rule ids"); ok = False
    if expect not in ("pass", "fail") or not name.startswith(f"{expect}-"):
        fail(f"{path}: expect {expect!r} does not match the file name"); ok = False
    if not (isinstance(v["description"], str) and v["description"].strip()):
        fail(f"{path}: description is empty"); ok = False
    kd = v.get("known_defect")
    if kd is not None and not (isinstance(kd, str) and DEFECT.match(kd)):
        fail(f"{path}: known_defect is not an ADP-D-NNN id"); ok = False
    if not ok:
        continue
    if expect == "fail":
        if len(rules) != 1:
            fail(f"{path}: a fail vector lists exactly one rule (§5.6.2)"); continue
        if ruledir != rules[0]:
            fail(f"{path}: directory {ruledir} is not its rule {rules[0]}"); continue
    elif ruledir != "_valid" and ruledir not in rules:
        fail(f"{path}: directory {ruledir} is not in its rules"); continue

    doc = t["doc"]
    cov = covered.setdefault(doc, {"pass": set(), "fail": set()})
    cov[expect].update(rules)

    got = verdict(doc, t["kind"], v["input"])
    if got is None:
        if kd is not None:
            fail(f"{path}: known_defect {kd} on a vector with no published schema")
        continue
    if kd is None:
        if got != expect:
            fail(f"{path}: schema says {got}, vector expects {expect}")
        continue
    st = status.get(kd)
    if st is None:
        fail(f"{path}: known_defect {kd} is not in DEFECTS.md")
    elif st != "OPEN":
        fail(f"{path}: known_defect {kd} is {st}; remove the marker (§5.6.4)")
    elif got == expect:
        fail(f"{path}: known_defect {kd} is stale; the schema now agrees (§5.6.4)")

for doc, cov in sorted(covered.items()):
    spec = Path("spec") / f"{doc}.md"
    if not spec.is_file():
        fail(f"conformance/{doc.lower()}: no spec/{doc}.md")
        continue
    for rule in RULE_ROW.findall(spec.read_text(encoding="utf-8")):
        for expect in ("pass", "fail"):
            if rule not in cov[expect]:
                fail(f"conformance/{doc.lower()}: {rule} has no {expect} vector (§5.6.3 rule 4)")

sys.exit(1 if failed else 0)
