def benchmark_row(output, reference):
    e=output.get("evidence_analysis",pd.DataFrame())
    r=output.get("retrieval",{})
    result=output.get("result",{}) or {}
    synthesis=output.get("synthesis",{}) or {}
    labels=e["nli_label"].value_counts().to_dict() if e is not None and not e.empty and "nli_label" in e.columns else {}
    return {
      "claim_id":reference["claim_id"],"claim":reference["claim"],
      "reference_label":reference["reference_label"],"reference_status":"curated_starter_not_expert_adjudicated",
      "reference_source_url":reference["reference_source_url"],
      "retrieval_status":r.get("status",""),"queries_attempted":len(r.get("query_logs",[])),
      "sources_retrieved":r.get("retrieved_count",0),
      "ranked_papers":len(output.get("ranked_papers",pd.DataFrame())),
      "candidate_passages":len(e) if e is not None else 0,
      "nli_entailment":labels.get("entailment",0),"nli_contradiction":labels.get("contradiction",0),
      "nli_neutral":labels.get("neutral",0),
      "provisional_direction":result.get("provisional_direction",""),
      "direct_answer":result.get("direct_answer",result.get("verdict","")),
      "workflow_status":result.get("status",""),
      "llm_used":bool(synthesis.get("llm_used",False)),
      "llm_status":synthesis.get("llm_status","unknown"),
      "llm_method":synthesis.get("method",""),
      "llm_model":synthesis.get("model",GEMINI_MODEL_NAME),
      "llm_error":synthesis.get("error",""),
      "llm_attempted_models":json.dumps(synthesis.get("attempted_models",[]),ensure_ascii=False),
      "elapsed_seconds":output.get("elapsed_seconds",None),
      "gold_relevant_source_ids":""
    }
