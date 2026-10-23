def supervisor_agent(claim_id, claim, print_steps=True):
    started=datetime.now(timezone.utc).isoformat(); clock=time.time(); trace=[]
    def log(step,details=None):
        trace.append({"step":step,"time_utc":datetime.now(timezone.utc).isoformat(),"details":details or {}})
        if print_steps: print(f"[{len(trace)}] {step}",details or "")
    scope=scope_safety_agent(claim); log("Scope & Safety Agent",scope)
    if not scope["allowed"]:
        retrieval={"status":"not_run","papers":[],"retrieved_count":0,"query_logs":[],"elapsed_seconds":0,"error":""}
        ranked=pd.DataFrame(); passages=pd.DataFrame(); evidence=pd.DataFrame()
        synthesis=llm_synthesis_agent(claim,evidence); result=decision_reporting_agent(claim,scope,retrieval,evidence,synthesis)
        return {"claim_id":claim_id,"claim":claim,"started_at_utc":started,"finished_at_utc":datetime.now(timezone.utc).isoformat(),
          "elapsed_seconds":round(time.time()-clock,3),"scope":scope,"queries":[],"retrieval":retrieval,
          "ranked_papers":ranked,"passages":passages,"evidence_analysis":evidence,"synthesis":synthesis,
          "result":result,"trace":trace,"environment":ENVIRONMENT}
    queries=query_planning_agent(claim); log("Query Planning Agent",{"queries":queries})
    retrieval=research_retriever_agent(queries); log("Europe PMC Retrieval Agent",{"status":retrieval["status"],"retrieved_count":retrieval["retrieved_count"],"query_logs":retrieval["query_logs"]})
    ranked=hybrid_rank_papers(claim,retrieval["papers"]); log("Hybrid Ranking Agent",{"ranked_papers":len(ranked),"mode":ranked["ranking_mode"].iloc[0] if not ranked.empty else "none"})
    passages=rank_candidate_passages(claim,ranked); log("Passage Extraction Agent",{"candidate_passages":len(passages)})
    evidence=citation_context_audit_agent(nli_evidence_agent(claim,passages)); log("NLI + Citation/Context Audit Agents",{"analyzed":len(evidence),"nli_counts":evidence["nli_label"].value_counts().to_dict() if not evidence.empty else {}})
    synthesis=llm_synthesis_agent(claim,evidence); log("LLM Synthesis Agent",{"method":synthesis["method"],"llm_used":synthesis["llm_used"],"llm_status":synthesis.get("llm_status","unknown"),"model":synthesis.get("model",GEMINI_MODEL_NAME),"error":synthesis.get("error","")})
    result=decision_reporting_agent(claim,scope,retrieval,evidence,synthesis); log("Conservative Decision Agent",{"status":result["status"]})
    return {"claim_id":claim_id,"claim":claim,"started_at_utc":started,"finished_at_utc":datetime.now(timezone.utc).isoformat(),
      "elapsed_seconds":round(time.time()-clock,3),"scope":scope,"queries":queries,"retrieval":retrieval,
      "ranked_papers":ranked,"passages":passages,"evidence_analysis":evidence,"synthesis":synthesis,
      "result":result,"trace":trace,"environment":ENVIRONMENT}
print("Supervisor ready.")
