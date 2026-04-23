import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.local_cbc_parser import parse_local_cbc_report

def precision_recall_f1(pred, gold):
    pred = set(pred)
    gold = set(gold)
    tp = len(pred & gold)
    fp = len(pred - gold)
    fn = len(gold - pred)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1

def run():
    base = ROOT / "tests" / "fixtures"
    expected = json.loads((base / "expected.json").read_text(encoding="utf-8-sig"))
    rows = []

    for item in expected:
        fixture = item["fixture"]
        text = (base / fixture).read_text(encoding="utf-8-sig")
        sex = "female"
        if "lipid" in fixture:
            sex = "male"

        result = parse_local_cbc_report(text, sex=sex)
        pred = [x["test"] for x in result["results"]]
        gold = item["expected_tests"]

        p, r, f1 = precision_recall_f1(pred, gold)
        rows.append({
            "fixture": fixture,
            "precision": round(p, 3),
            "recall": round(r, 3),
            "f1": round(f1, 3),
            "num_pred": len(pred),
            "num_gold": len(gold),
            "pred": pred,
            "gold": gold
        })

    out_path = base / "benchmark_results.json"
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps(rows, indent=2))

if __name__ == "__main__":
    run()
