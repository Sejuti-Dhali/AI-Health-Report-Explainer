import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.local_cbc_parser import parse_local_cbc_report

FIXTURES = [
    ("cbc_sample.txt", "female"),
    ("lipid_sample.txt", "male"),
    ("diabetes_sample.txt", "female"),
    ("kidney_sample.txt", "female"),
    ("thyroid_sample.txt", "female"),
]

def run():
    base = ROOT / "tests" / "fixtures"
    out = []
    for name, sex in FIXTURES:
        text = (base / name).read_text(encoding="utf-8")
        result = parse_local_cbc_report(text, sex=sex)
        out.append({
            "fixture": name,
            "sex": sex,
            "num_results": len(result["results"]),
            "risk_level": result["risk_level"],
            "tests": [x["test"] for x in result["results"]],
        })
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    run()
