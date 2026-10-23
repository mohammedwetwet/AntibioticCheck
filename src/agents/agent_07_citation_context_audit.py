def citation_context_audit_agent(df):
    if df.empty: return df.copy()
    df=df.copy()
    df["has_source_identifier"]=df.apply(lambda r: bool(str(r.get("pmid","")).strip() or str(r.get("pmcid","")).strip()
        or str(r.get("doi","")).strip() or str(r.get("url","")).startswith("http")),axis=1)
    df["has_passage"]=df["candidate_sentence"].astype(str).str.len().gt(0)
    df["metadata_check"]=np.where(df["has_source_identifier"] & df["has_passage"],
                                  "identifier_and_passage_present_only","missing_identifier_or_passage")
    df["requires_human_context_review"]=df["context_flags"].astype(str).str.len().gt(0)
    df["human_relevance"]=""; df["human_stance"]=""; df["reviewer_rationale"]=""
    # Metadata presence never means the passage has been independently verified.
    df["citation_support_verified"]=False
    # A transparent grouping aid; not a final truth label.
    df["evidence_group"]=df["nli_label"].map({
        "entailment":"provisionally_supports_claim",
        "contradiction":"provisionally_contradicts_claim",
        "neutral":"neutral_or_unclear"
    }).fillna("unclassified")
    df["needs_context_review"]=df["requires_human_context_review"] | df["nli_label"].isin(["analysis_error","model_unavailable"])
    return df
