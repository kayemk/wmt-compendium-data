from pathlib import Path
import json
import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCHEMAS = ROOT / "schemas"

def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))

WAR_BAND_SCHEMA = load_schema("warband.schema.json")
UNIT_SCHEMA = load_schema("unit.schema.json")

def load_yaml_files(folder: Path) -> list[dict]:
    items = []
    for p in sorted(folder.glob("*.yml")):
        obj = yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            raise ValueError(f"{p} must contain a YAML mapping/object")
        obj["_file"] = str(p.relative_to(ROOT))
        items.append(obj)
    return items

def ensure_unique_ids(items: list[dict], kind: str):
    seen = {}
    for it in items:
        _id = it.get("id")
        if not _id:
            raise ValueError(f"Missing id in {it.get('_file')}")
        if _id in seen:
            raise ValueError(f"Duplicate {kind} id '{_id}' in {seen[_id]} and {it['_file']}")
        seen[_id] = it["_file"]

def main():
    warbands = load_yaml_files(DATA / "warbands")
    units = load_yaml_files(DATA / "units")

    ensure_unique_ids(warbands, "warband")
    ensure_unique_ids(units, "unit")

    unit_ids = {u["id"] for u in units}
    warband_ids = {w["id"] for w in warbands}

    for w in warbands:
        inst = {k: v for k, v in w.items() if k != "_file"}
        validate(instance=inst, schema=WAR_BAND_SCHEMA)
        missing = [uid for uid in w["unit_ids"] if uid not in unit_ids]
        if missing:
            raise ValueError(f"{w['_file']} references missing unit_ids: {missing}")

    for u in units:
        inst = {k: v for k, v in u.items() if k != "_file"}
        validate(instance=inst, schema=UNIT_SCHEMA)
        missing = [wid for wid in u["warband_ids"] if wid not in warband_ids]
        if missing:
            raise ValueError(f"{u['_file']} references missing warband_ids: {missing}")

    print("OK: validation passed")

if __name__ == "__main__":
    main()
