def extractive_summary(claim, df, max_items=4):
    if df is None or df.empty: return "No candidate passages were retrieved. This does not prove that no evidence exists."
    lines=[]
    for _, r in df.head(max_items).iterrows():
        lines.append(f"- [{r.get('source_id','')}] {r.get('title','')}: {r.get('candidate_sentence','')} (stance signal: {r.get('nli_label','unknown')})")
    return "Extractive overview only; not a factual verdict. Read each passage in context.\\n" + "\\n".join(lines)

def llm_synthesis_agent(claim, df):
    fallback=extractive_summary(claim, df)
    if not LLM_ENABLED:
        return {"summary":fallback,"method":"extractive_fallback_no_api_key","llm_used":False,"llm_status":"disabled_no_api_key","error":"","model":GEMINI_MODEL_NAME,"attempted_models":[]}
    items=[]
    for _, r in df.head(6).iterrows():
        items.append({"source_id":r.get("source_id",""),"title":r.get("title",""),"url":r.get("url",""),"passage":r.get("candidate_sentence",""),"nli_signal":r.get("nli_label","unknown"),"context_flags":r.get("context_flags",""),"stance_method":r.get("stance_method","gemma_api")})
    prompt=("Summarize only supplied evidence passages for a research prototype. Do not add outside facts or provide medical advice. Do not decide whether the claim is true. Distinguish direct evidence from prescribing patterns, survey findings, or indirect context. Mention disagreement and cite source_id for each point. Plain text only.\\nCLAIM: "+claim+"\\nPASSAGES_JSON:\\n"+json.dumps(items,ensure_ascii=False))
    try:
        response=get_genai_client().models.generate_content(model=GEMINI_MODEL_NAME, contents=prompt)
        summary=str(getattr(response,"text","") or "").strip()
        if not summary: raise RuntimeError("Gemma returned an empty synthesis.")
        return {"summary":summary,"method":GEMINI_MODEL_NAME,"llm_used":True,"llm_status":"success","error":"","model":GEMINI_MODEL_NAME,"attempted_models":[{"model":GEMINI_MODEL_NAME,"status":"success"}]}
    except Exception as exc:
        return {"summary":fallback,"method":"extractive_fallback_after_api_error","llm_used":False,"llm_status":"error","error":str(exc)[:700],"model":GEMINI_MODEL_NAME,"attempted_models":[{"model":GEMINI_MODEL_NAME,"status":"error"}]}
