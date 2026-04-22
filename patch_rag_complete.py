from pathlib import Path
import re

repo_root = Path(".").resolve()
backend = repo_root / "backend"
frontend = repo_root / "frontend"

def find_backend_upload_file():
    candidates = []
    for p in backend.rglob("*.py"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        score = 0
        if "/api/upload" in txt: score += 3
        if "upload_report" in txt: score += 3
        if "results.append" in txt: score += 2
        if "summary" in txt: score += 1
        if score:
            candidates.append((score, p))
    candidates.sort(reverse=True)
    return candidates[0][1] if candidates else None

def patch_backend(upload_file: Path):
    txt = upload_file.read_text(encoding="utf-8", errors="ignore")

    if "from services.rag.rag_pipeline import run_rag_pipeline" not in txt:
        txt = "from services.rag.rag_pipeline import run_rag_pipeline\n" + txt

    if "def _rag_enrich_result(" not in txt:
        helper = '''
def _rag_enrich_result(item: dict, llm_callable):
    patient_result = {
        "test": item.get("test", ""),
        "value": item.get("value", ""),
        "unit": item.get("unit", ""),
        "reference": item.get("reference", ""),
    }
    rag_result = run_rag_pipeline(patient_result, llm_callable)

    item["status"] = rag_result.get("final_status", item.get("status", "unknown"))
    item["explanation"] = rag_result.get("final_explanation", item.get("explanation", ""))
    item["confidence_score"] = rag_result.get("confidence", {}).get("confidence")
    item["confidence_band"] = rag_result.get("confidence", {}).get("confidence_band")
    item["vote_ratio"] = rag_result.get("confidence", {}).get("vote_ratio")
    item["semantic_agreement"] = rag_result.get("confidence", {}).get("semantic_agreement")
    item["needs_manual_review"] = rag_result.get("needs_manual_review", False)
    item["retrieved_evidence"] = rag_result.get("retrieved_evidence", [])
    item["hallucination_flag"] = rag_result.get("hallucination", {}).get("hallucination_flag", False)
    item["evidence_support"] = rag_result.get("hallucination", {}).get("evidence_support", False)
    item["evidence_support_score"] = rag_result.get("hallucination", {}).get("evidence_support_score", 0.0)
    return item
'''
        txt += "\n\n" + helper + "\n"

    if "results.append(_rag_enrich_result(" not in txt:
        txt = re.sub(
            r"results\.append\((.*?)\)",
            r"results.append(_rag_enrich_result(\1, llm_callable))",
            txt,
            count=1,
            flags=re.DOTALL
        )

    if "llm_callable" not in txt and "Groq" in txt:
        txt += "\n# NOTE: Ensure llm_callable points to your existing Groq wrapper.\n"

    upload_file.write_text(txt, encoding="utf-8")
    print(f"[backend] patched: {upload_file}")

def find_frontend_page():
    candidates = []
    for p in (frontend / "src").rglob("*.jsx"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        score = 0
        name = p.name.lower()
        if "result" in name: score += 3
        if "analysis" in name: score += 3
        if "upload" in name: score += 2
        if "results" in txt.lower(): score += 2
        if "summary" in txt.lower(): score += 1
        if score:
            candidates.append((score, p))
    candidates.sort(reverse=True)
    return candidates[0][1] if candidates else None

def patch_frontend(page_file: Path):
    txt = page_file.read_text(encoding="utf-8", errors="ignore")

    imports = [
        'import ConfidenceBadge from "../components/ConfidenceBadge";',
        'import ManualReviewBadge from "../components/ManualReviewBadge";',
        'import EvidenceList from "../components/EvidenceList";',
        'import WarningChip from "../components/WarningChip";',
        'import { normalizeResultForUi } from "../utils/ragUi";',
    ]
    for imp in imports:
        if imp not in txt:
            txt = imp + "\n" + txt

    if "RAG_SAFETY_UI_BLOCK" not in txt:
        txt += '''

{/* RAG_SAFETY_UI_BLOCK */}
{/* Place this block inside each rendered test-result card and replace `item` with your row variable if needed */}
{(() => {
  const r = normalizeResultForUi(item);
  return (
    <div className="mt-3">
      <div className="flex flex-wrap gap-2">
        <ConfidenceBadge band={r.confidence_band} score={r.confidence_score} />
        <ManualReviewBadge show={r.needs_manual_review} />
        <WarningChip show={r.hallucination_flag || !r.evidence_support} text="Low evidence support" />
      </div>

      {(r.needs_manual_review || r.hallucination_flag || !r.evidence_support) ? (
        <div className="mt-2 rounded-lg border border-amber-200 bg-amber-50 p-2 text-xs text-amber-800">
          Interpretation uncertainty is elevated. Review with a clinician is recommended.
        </div>
      ) : null}

      <EvidenceList evidence={r.retrieved_evidence || []} />
    </div>
  );
})()}
'''
    page_file.write_text(txt, encoding="utf-8")
    print(f"[frontend] patched: {page_file}")

upload_file = find_backend_upload_file()
if upload_file:
    patch_backend(upload_file)
else:
    print("[backend] upload file not found automatically.")

page_file = find_frontend_page()
if page_file:
    patch_frontend(page_file)
else:
    print("[frontend] result page not found automatically.")
