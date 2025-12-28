#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCHEMAS = ROOT / "schemas"

ID_RE = re.compile(r"^[a-z0-9-]+$")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_yaml_file(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: YAML root must be a mapping/object.")
    return data


def load_dir(folder: Path) -> list[dict]:
    items: list[dict] = []
    for fp in sorted(folder.glob("*.yml")):
        d = read_yaml_file(fp)
        d["_file"] = str(fp)
        items.append(d)
    return items


def validate_schema(items: list[dict], schema: dict, kind: str) -> None:
    v = Draft202012Validator(schema)
    for it in items:
        payload = {k: v for k, v in it.items() if not k.startswith("_")}
        errors = sorted(v.iter_errors(payload), key=lambda e: list(e.path))
        if errors:
            msg = "\n".join([f"  - {list(e.path)}: {e.message}" for e in errors[:20]])
            raise ValueError(f"{kind} schema errors in {it.get('_file')}:\n{msg}")


def ensure_id_and_filename(items: list[dict], kind: str) -> None:
    for it in items:
        fp = Path(it["_file"])
        _id = it.get("id")
        if not isinstance(_id, str) or not _id.strip():
            raise ValueError(f"{fp}: missing required 'id'")
        if not ID_RE.fullmatch(_id):
            raise ValueError(f"{fp}: invalid id '{_id}' (allowed: a-z 0-9 '-')")
        if fp.stem != _id:
            raise ValueError(f"{fp}: filename must match id '{_id}' (expected {fp.with_name(_id + fp.suffix)})")


def ensure_unique_ids(items: list[dict], kind: str) -> None:
    seen: set[str] = set()
    for it in items:
        _id = it["id"]
        if _id in seen:
            raise ValueError(f"Duplicate {kind} id: '{_id}'")
        seen.add(_id)


def ensure_refs(warbands: list[dict], units: list[dict]) -> None:
    warband_ids = {w["id"] for w in warbands}
    unit_ids = {u["id"] for u in units}

    for w in warbands:
        fp = w["_file"]
        for uid in (w.get("unit_ids") or []):
            if uid not in unit_ids:
                raise ValueError(f"{fp}: unit_ids references unknown unit id '{uid}'")

    for u in units:
        fp = u["_file"]
        for wid in (u.get("warband_ids") or []):
            if wid not in warband_ids:
                raise ValueError(f"{fp}: warband_ids references unknown warband id '{wid}'")


def main() -> int:
    warbands = load_dir(DATA / "warbands")
    units = load_dir(DATA / "units")

    warband_schema = read_json(SCHEMAS / "warband.schema.json")
    unit_schema = read_json(SCHEMAS / "unit.schema.json")

    validate_schema(warbands, warband_schema, "warband")
    validate_schema(units, unit_schema, "unit")

    ensure_id_and_filename(warbands, "warband")
    ensure_id_and_filename(units, "unit")

    ensure_unique_ids(warbands, "warband")
    ensure_unique_ids(units, "unit")

    ensure_refs(warbands, units)

    print("OK: validation passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1)
EOF
