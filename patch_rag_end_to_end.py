from pathlib import Path
import re

repo_root = Path(".").resolve()
backend = repo_root / "backend"
frontend = repo_root / "frontend"

# ---------- BACKEND PATCH ----------
py_files = list(backend.rglob("*.py"))
upload_file = None
for p in py_files:
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if "/api/upload" in txt or "upload_report" in txt or "results.append" in txt:
        upload_file = p
        break

if upload_file:
    txt = upload_file.read_text(encoding="utf-8", errors="ignore")

    if "from services.rag.rag_pipeline import run_rag_pipeline" not in txt:
        txt = "from services.rag.rag_pipeline import run_rag_pipeline\n" + txt

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
    if "_rag_enrich_result" not in txt:
        txt += "\n\n" + helper + "\n"

    if "results.append(_rag_enrich_result(" not in txt:
        txt = re.sub(
            r"results\.append\((.*?)\)",
            r"results.append(_rag_enrich_result(\1, llm_callable))",
            txt,
            count=1,
            flags=re.DOTALL
        )

    upload_file.write_text(txt, encoding="utf-8")
    print(f"[backend] patched: {upload_file}")
else:
    print("[backend] upload file not auto-detected; manual patch may be needed.")

# ---------- FRONTEND PATCH ----------
jsx_files = list((frontend / "src").rglob("*.jsx"))
page_file = None
for p in jsx_files:
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if "analysis" in p.name.lower() or "result" in p.name.lower() or "upload" in p.name.lower() or "results" in txt.lower():
        page_file = p
        break

if page_file:
    txt = page_file.read_text(encoding="utf-8", errors="ignore")

    imports = [
        'import ConfidenceBadge from "../components/ConfidenceBadge";',
        'import ManualReviewBadge from "../components/ManualReviewBadge";',
        'import EvidenceList from "../components/EvidenceList";',
        'import { normalizeResultForUi } from "../utils/ragUi";',
    ]
    for imp in imports:
        if imp not in txt:
            txt = imp + "\n" + txt

    if "normalizeResultForUi(" not in txt:
        txt = txt.replace("results.map((item", "results.map((item")
        txt = txt.replace("results.map((item) =>", "results.map((item) => { const r = normalizeResultForUi(item); return (")
        txt = txt.replace("))}", "))})" if "))}" in txt else txt)

    append_block = '''
{/* RAG safety UI */}
<div className="mt-2 flex flex-wrap gap-2">
  <ConfidenceBadge band={r?.confidence_band} score={r?.confidence_score} />
  <ManualReviewBadge show={r?.needs_manual_review} />
  {r?.hallucination_flag ? (
    <span className="inline-flex items-center rounded-full border border-red-200 bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700">
      Low evidence support
    </span>
  ) : null}
</div>
<EvidenceList evidence={r?.retrieved_evidence || []} />
'''
    if "RAG safety UI" not in txt:
        txt += "\n\n" + append_block + "\n"

    page_file.write_text(txt, encoding="utf-8")
    print(f"[frontend] patched: {page_file}")
else:
    print("[frontend] results page not auto-detected; manual patch may be needed.")
