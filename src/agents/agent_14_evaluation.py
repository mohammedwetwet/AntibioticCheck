from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

def recall_at_k(retrieved_source_ids,gold_relevant_source_ids,k=5):
    gold={str(x).strip() for x in gold_relevant_source_ids if str(x).strip()}
    if not gold:return None
    got=[str(x).strip() for x in list(retrieved_source_ids)[:k]]
    return len(set(got)&gold)/len(gold)

def evaluate_reviewed_stance(df,gold_col="human_stance",predicted_col="nli_label"):
    needed={gold_col,predicted_col}
    if not needed.issubset(df.columns): raise ValueError(f"Missing columns: {needed-set(df.columns)}")
    valid={"supports_claim","contradicts_claim","neutral_or_unclear"}
    clean=df.copy()
    clean[gold_col]=clean[gold_col].astype(str).str.strip().str.lower()
    clean[predicted_col]=clean[predicted_col].astype(str).str.strip().str.lower()
    clean=clean[clean[gold_col].isin(valid)&clean[predicted_col].isin({"entailment","contradiction","neutral"})]
    mapping={"supports_claim":"entailment","contradicts_claim":"contradiction","neutral_or_unclear":"neutral"}
    if clean.empty:return {"status":"not_calculated","reason":"No valid human-reviewed stance labels."}
    y=clean[gold_col].map(mapping); pred=clean[predicted_col]
    return {"status":"calculated_from_reviewed_rows","n":len(clean),
      "accuracy":float(accuracy_score(y,pred)),
      "macro_f1":float(f1_score(y,pred,average="macro",zero_division=0)),
      "report":classification_report(y,pred,zero_division=0,output_dict=True)}

def calculate_benchmark_metrics(results_df):
    """Operational metrics always; reference agreement is exploratory because starter labels are not expert-adjudicated."""
    if results_df is None or results_df.empty:
        return {"operational":{"status":"not_calculated","reason":"No benchmark rows."},
                "claim_reference_agreement":{"status":"not_calculated","reason":"No benchmark rows."},
                "reviewed_gold_metrics":{"status":"not_calculated","reason":"No human-reviewed labels."}}
    n=len(results_df)
    elapsed=pd.to_numeric(results_df.get("elapsed_seconds",pd.Series(dtype=float)),errors="coerce")
    retrieval=results_df.get("retrieval_status",pd.Series([""]*n)).astype(str)
    llm_used=results_df.get("llm_used",pd.Series([False]*n)).fillna(False).astype(bool)
    op={
      "status":"calculated",
      "claims_attempted":int(n),
      "retrieval_success_count":int(retrieval.eq("success").sum()),
      "retrieval_success_rate":float(retrieval.eq("success").mean()),
      "mean_sources_retrieved":float(pd.to_numeric(results_df.get("sources_retrieved",0),errors="coerce").mean()),
      "mean_ranked_papers":float(pd.to_numeric(results_df.get("ranked_papers",0),errors="coerce").mean()),
      "mean_candidate_passages":float(pd.to_numeric(results_df.get("candidate_passages",0),errors="coerce").mean()),
      "mean_elapsed_seconds":float(elapsed.mean()) if elapsed.notna().any() else None,
      "llm_success_count":int(llm_used.sum()),
      "llm_success_rate_among_claims":float(llm_used.mean()),
      "llm_error_count":int(results_df.get("llm_status",pd.Series([""]*n)).astype(str).eq("error").sum()),
      "workflow_error_count":int(results_df.get("workflow_status",pd.Series([""]*n)).astype(str).eq("workflow_error").sum())
    }
    # Preserve the context-dependent class instead of silently excluding it from evaluation.
    ref_map={"SUPPORTED":"supports_claim","CONTRADICTED":"contradicts_claim",
             "CONTEXT_DEPENDENT":"context_dependent"}
    evaluable_labels=["supports_claim","contradicts_claim","context_dependent"]
    eval_df=results_df.copy()
    eval_df["expected_direction"]=eval_df.get("reference_label",pd.Series([""]*n)).astype(str).str.upper().map(ref_map)
    eval_df["predicted_direction"]=eval_df.get("provisional_direction",pd.Series([""]*n)).astype(str)
    eval_df=eval_df[eval_df["expected_direction"].notna() & eval_df["predicted_direction"].isin(evaluable_labels)]
    if len(eval_df):
        y=eval_df["expected_direction"]; pred=eval_df["predicted_direction"]
        ref={
          "status":"exploratory_only_curated_starter_labels_not_expert_adjudicated",
          "evaluation_classes":evaluable_labels,
          "n_scored":int(len(eval_df)),"n_abstained_or_mixed":int(n-len(eval_df)),
          "accuracy_on_scored":float(accuracy_score(y,pred)),
          "macro_f1_on_scored":float(f1_score(y,pred,labels=evaluable_labels,average="macro",zero_division=0)),
          "coverage":float(len(eval_df)/n),
          "reference_class_counts":eval_df["expected_direction"].value_counts().to_dict(),
          "prediction_class_counts":eval_df["predicted_direction"].value_counts().to_dict(),
          "classification_report":classification_report(y,pred,labels=evaluable_labels,zero_division=0,output_dict=True)
        }
    else:
        ref={"status":"not_calculated","reason":"No benchmark rows had both a supported reference class and an evaluable prediction.",
             "evaluation_classes":evaluable_labels,"n_scored":0,"n_abstained_or_mixed":int(n),"coverage":0.0}
    return {"operational":op,"claim_reference_agreement":ref,
            "reviewed_gold_metrics":{"status":"not_calculated","reason":"Requires independently reviewed gold labels and relevant source IDs."}}
