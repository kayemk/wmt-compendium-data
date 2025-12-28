from pathlib import Path
import json
import shutil
import subprocess
import sys
import yaml
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"
DIST = ROOT / "dist"

def load_folder(folder: Path) -> list[dict]:
    out = []
    for p in sorted(folder.glob("*.yml")):
        out.append(yaml.safe_load(p.read_text(encoding="utf-8")))
    return out

def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "validate.py")])

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    shutil.copytree(SITE, DIST, dirs_exist_ok=True)

    warbands = load_folder(DATA / "warbands")
    units = load_folder(DATA / "units")

    write_json(DIST / "api" / "warbands.json", warbands)
    write_json(DIST / "api" / "units.json", units)

    for w in warbands:
        write_json(DIST / "api" / "warbands" / f"{w['id']}.json", w)
    for u in units:
        write_json(DIST / "api" / "units" / f"{u['id']}.json", u)

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "counts": {"warbands": len(warbands), "units": len(units)}
    }
    write_json(DIST / "api" / "index.json", meta)

    print("OK: dist/ generated")

if __name__ == "__main__":
    main()
