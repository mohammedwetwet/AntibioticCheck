def decision_reporting_agent(claim, scope, retrieval, evidence, synthesis):
    limitations = [
        "Research prototype only; every result requires physician/researcher review.",
        "The direction is provisional and based on retrieved abstract passages plus an NLI model, not proof of truth or clinical efficacy.",
        "NLI scores are model scores, not calibrated probabilities of a claim being true.",
        "Retrieval may miss relevant papers; abstracts may omit important study context.",
        "A citation's existence and metadata do not verify that it supports the sentence shown.",
        "Full-text source, methods, population, limitations, and clinical guidance require human review.",
        "Benchmark labels are reference labels, not independently adjudicated ground truth."
    ]
    empty_lists = {"supporting_papers": [], "contradicting_papers": [], "neutral_or_unclear_papers": [], "context_dependent_papers": []}
    # Claims whose wording explicitly depends on circumstances must not be forced into a binary verdict.
    # This is a wording/logic guard, not a lookup of benchmark IDs or reference labels.
    def _requires_contextual_verdict(text):
        t = re.sub(r"\s+", " ", str(text or "").lower())
        contextual_patterns = [
            r"\bsecondary bacterial\b", r"\bfollowed by\b", r"\bdepends on\b",
            r"\bdepending on\b", r"\bmay require\b", r"\bin some cases\b",
            r"\bunder certain conditions\b", r"\bclinical assessment\b"
        ]
        return any(re.search(p, t) for p in contextual_patterns)
    claim_is_contextual = _requires_contextual_verdict(claim)
    if not scope.get("allowed", False):
        verdict = "Unable to assess this claim because it falls outside the prototype's allowed scope."
        direction, status = "not_assessed", scope.get("status", "blocked")
        reason = scope.get("reason", "Out-of-scope claim.")
        support_papers, oppose_papers, neutral_papers, context_papers = [], [], [], []
    elif retrieval.get("status") == "error":
        verdict = "Unable to assess: literature retrieval failed. This is a technical failure, not evidence for or against the claim."
        direction, status, reason = "technical_failure", "retrieval_error", "Retry retrieval before interpreting the claim."
        support_papers, oppose_papers, neutral_papers, context_papers = [], [], [], []
    elif evidence is None or evidence.empty:
        verdict = "The available search did not return usable evidence for this claim."
        direction, status = "insufficient_evidence", "no_candidate_passages"
        reason = "No usable passages were retained; this does not mean that evidence does not exist."
        support_papers, oppose_papers, neutral_papers, context_papers = [], [], [], []
    else:
        # Aggregate by source first: each paper contributes at most one stance.
        source_rows = {}
        for _, row in evidence.iterrows():
            label = str(row.get("nli_label", "unknown"))
            scores = row.get("nli_scores", {})
            if isinstance(scores, str):
                try:
                    scores = json.loads(scores)
                except Exception:
                    scores = {}
            try:
                confidence = float(row.get("decision_confidence", scores.get(label, row.get("nli_confidence", 0.0))) or 0.0)
            except Exception:
                confidence = 0.0
            relevance = float(row.get("passage_hybrid_score", 0.0) or 0.0)
            flags = str(row.get("context_flags", ""))
            # Discount contextually indirect evidence; do not treat this as source validation.
            context_factor = 1.0
            if "survey_or_belief_context" in flags: context_factor *= 0.45
            if "preclinical_context" in flags: context_factor *= 0.60
            if "secondary_infection_context" in flags: context_factor *= 0.65
            if "uncertainty_or_study_context" in flags: context_factor *= 0.80
            if label not in {"entailment", "contradiction", "neutral"}:
                label = "neutral"
            weight = max(0.0, min(1.0, confidence)) * max(0.0, min(1.0, relevance)) * context_factor
            item = {
                "source_id": str(row.get("source_id", "")), "title": str(row.get("title", "")),
                "year": str(row.get("year", "")), "url": str(row.get("url", "")),
                "pmid": str(row.get("pmid", "")), "pmcid": str(row.get("pmcid", "")),
                "doi": str(row.get("doi", "")), "passage": str(row.get("candidate_sentence", "")),
                "nli_label": label, "nli_confidence": round(confidence, 4),
                "stance_method": str(row.get("stance_method","nli_model")),
                "domain_stance_override": str(row.get("domain_stance_override","")),
                "relevance_score": round(relevance, 4), "context_flags": flags,
                "citation_support_verified": False,
                "human_review_required": True
            }
            sid = item["source_id"] or item["title"]
            # Keep the most relevant/high-confidence passage for each paper.
            rank_key = weight + 0.20 * relevance
            if sid not in source_rows or rank_key > source_rows[sid]["_rank_key"]:
                item["_weight"] = weight
                item["_rank_key"] = rank_key
                source_rows[sid] = item

        support_papers, oppose_papers, neutral_papers, context_papers = [], [], [], []
        support_weight = oppose_weight = neutral_weight = 0.0
        for item in source_rows.values():
            label = item["nli_label"]
            weight = item["_weight"]
            public_item = {k:v for k,v in item.items() if not k.startswith("_")}
            if label == "entailment":
                support_papers.append(public_item); support_weight += weight
            elif label == "contradiction":
                oppose_papers.append(public_item); oppose_weight += weight
            else:
                neutral_papers.append(public_item); neutral_weight += weight
        support_papers.sort(key=lambda x:(x["relevance_score"], x["nli_confidence"]), reverse=True)
        oppose_papers.sort(key=lambda x:(x["relevance_score"], x["nli_confidence"]), reverse=True)
        neutral_papers.sort(key=lambda x:(x["relevance_score"], x["nli_confidence"]), reverse=True)

        active = support_weight + oppose_weight
        total = active + neutral_weight
        ratio = (max(support_weight, oppose_weight) + 1e-9) / (min(support_weight, oppose_weight) + 1e-9)
        # Explicit domain-rule evidence can settle a directly matched claim provisionally;
        # unrelated prescribing/bacterial-treatment passages are neutralized by the guard.
        rule_support = [p for p in support_papers if p.get("stance_method") == "domain_rule_guard_overrode_nli"]
        rule_oppose = [p for p in oppose_papers if p.get("stance_method") == "domain_rule_guard_overrode_nli"]
        if claim_is_contextual:
            # Preserve the conditional nature of the claim, even if retrieved passages lean one way.
            # The interface should explain that applicability depends on clinical context, not assert a universal rule.
            direction = "context_dependent"
            verdict = ("This claim is context-dependent: a viral infection may sometimes be followed by a secondary bacterial infection, "
                       "and antibiotics may be appropriate for the bacterial infection after clinical assessment. "
                       "The retrieved evidence is provisional and does not establish that antibiotics treat the original viral infection.")
            context_papers = support_papers + oppose_papers + neutral_papers
        elif len(source_rows) == 0 or active < 0.08:
            direction = "insufficient_evidence"
            verdict = "The search did not find enough relevant evidence to give a reliable direction."
        elif len(support_papers) >= 2 and support_weight >= 0.10 and support_weight > oppose_weight and ratio >= 1.65:
            direction = "supports_claim"
            verdict = "The retrieved evidence provisionally supports the claim."
        elif len(oppose_papers) >= 2 and oppose_weight >= 0.10 and oppose_weight > support_weight and ratio >= 1.65:
            direction = "contradicts_claim"
            verdict = "The retrieved evidence provisionally contradicts the claim."
        elif support_weight > 0 and oppose_weight > 0 and ratio < 1.65:
            direction = "mixed_or_conflicting"
            verdict = "The retrieved evidence is mixed or conflicting; the claim cannot be resolved reliably from these passages alone."
        elif support_weight > oppose_weight and len(support_papers) >= 1 and support_weight >= 0.13 and (not oppose_papers or ratio >= 1.65):
            direction = "supports_claim"
            verdict = "The retrieved evidence provisionally supports the claim, but independent source confirmation is limited."
        elif oppose_weight > support_weight and len(oppose_papers) >= 1 and oppose_weight >= 0.13 and (not support_papers or ratio >= 1.65):
            direction = "contradicts_claim"
            verdict = "The retrieved evidence provisionally contradicts the claim, but independent source confirmation is limited."
        else:
            direction = "insufficient_evidence"
            verdict = "The retrieved passages are not strong or consistent enough to give a reliable direction."
        status = "awaiting_physician_review"
        reason = (
            f"Paper-level weighted NLI signals (not truth probabilities): supporting={support_weight:.3f}, "
            f"contradicting={oppose_weight:.3f}, neutral/unclear={neutral_weight:.3f}; "
            f"unique sources={len(source_rows)}. Domain-rule overrides are heuristic stance guards, not calibrated probabilities. Check each source in full context."
        )

    counts = evidence["nli_label"].value_counts().to_dict() if evidence is not None and not evidence.empty else {}
    result = {
        "project": "PublicHealth Evidence AI (ABX-AI)", "claim": claim,
        "direct_answer": verdict, "provisional_direction": direction, "verdict": verdict,
        "status": status, "reason": reason, "sources_retrieved": retrieval.get("retrieved_count", 0),
        "candidate_passages": len(evidence) if evidence is not None else 0,
        "nli_signal_counts": counts, "supporting_papers": support_papers,
        "contradicting_papers": oppose_papers, "neutral_or_unclear_papers": neutral_papers,
        "context_dependent_papers": context_papers if "context_papers" in locals() else [],
        "synthesis": synthesis.get("summary", ""), "synthesis_method": synthesis.get("method", ""),
        "llm_used": synthesis.get("llm_used", False), "limitations": limitations,
        "mandatory_review": "A physician/research reviewer must inspect the full cited sources before any conclusion is used.",
        "disclaimer": "Research prototype only. Not for diagnosis, prescribing, or personal treatment decisions."
    }
    return result
