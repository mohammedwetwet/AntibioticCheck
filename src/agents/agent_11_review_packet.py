REVIEW_COLUMNS=["claim_id","claim","source_id","title","year","doi","pmid","pmcid","url","candidate_sentence",
 "paper_hybrid_score","passage_hybrid_score","nli_label","nli_scores","context_flags","metadata_check",
 "citation_support_verified","human_relevance","human_stance","reviewer_rationale"]
def create_review_packet(output,path):
    df=output.get("evidence_analysis",pd.DataFrame()).copy()
    if df.empty: df=pd.DataFrame(columns=REVIEW_COLUMNS)
    else:
        df["claim_id"]=output.get("claim_id",""); df["claim"]=output.get("claim","")
        for col in REVIEW_COLUMNS:
            if col not in df.columns: df[col]=""
        df=df[REVIEW_COLUMNS]
    df.to_csv(path,index=False); return df
