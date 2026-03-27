import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "benchmark_ranges.json"
SOURCE_PATH = Path(__file__).resolve().parent.parent / "data" / "source_registry.json"


def load_benchmarks():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sources():
    with open(SOURCE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
