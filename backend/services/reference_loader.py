import json
from pathlib import Path

REFERENCE_DIR = Path("data/reference_ranges")

def load_reference_file(name: str):
    path = REFERENCE_DIR / f"{name}.json"
    if not path.exists():
        return []
    # utf-8-sig handles BOM safely
    return json.loads(path.read_text(encoding="utf-8-sig"))

def load_all_reference_specs():
    specs = []
    for name in ["cbc", "lipid", "diabetes", "thyroid", "kidney", "liver"]:
        specs.extend(load_reference_file(name))
    return specs
