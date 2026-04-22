export function normalizeResultForUi(result) {
  return {
    ...result,
    confidence_band: result?.confidence_band || "low",
    confidence_score: typeof result?.confidence_score === "number" ? result.confidence_score : null,
    vote_ratio: typeof result?.vote_ratio === "number" ? result.vote_ratio : null,
    semantic_agreement: typeof result?.semantic_agreement === "number" ? result.semantic_agreement : null,
    hallucination_flag: !!result?.hallucination_flag,
    evidence_support: !!result?.evidence_support,
    evidence_support_score: typeof result?.evidence_support_score === "number" ? result.evidence_support_score : null,
    retrieved_evidence: result?.retrieved_evidence || [],
    needs_manual_review: !!result?.needs_manual_review,
  };
}
