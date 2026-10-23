def _minmax(values):
    values = np.asarray(values, dtype=float)
    if len(values) == 0: return values
    lo, hi = float(np.min(values)), float(np.max(values))
    return (values-lo)/(hi-lo+1e-9)

def paper_quality_prior(paper):
    """Small, transparent prior; never treated as proof of truth."""
    text = (str(paper.get("title","")) + " " + str(paper.get("publication_types",""))).lower()
    prior = 0.0
    if "systematic review" in text or "meta-analysis" in text: prior += 0.06
    if "randomized controlled trial" in text or "randomised controlled trial" in text: prior += 0.04
    if "case report" in text or "editorial" in text or "letter" in text: prior -= 0.04
    try:
        year = int(str(paper.get("year",""))[:4])
        if year >= 2020: prior += 0.02
    except Exception:
        pass
    return float(np.clip(prior, -0.06, 0.08))

def hybrid_rank_papers(claim, papers, top_n=MAX_PAPERS_TO_RANK):
    """BM25 + transparent metadata prior; intentionally no local embedding model."""
    if not papers: return pd.DataFrame()
    docs = [(p.get("title","")+" "+p.get("abstract","")).strip() for p in papers]
    tokenized = [tokenize(x) for x in docs]
    query_tokens = [t for t in tokenize(claim) if t not in STOPWORDS]
    if not query_tokens or not any(tokenized): return pd.DataFrame()
    bm_raw = np.asarray(BM25Okapi(tokenized).get_scores(query_tokens), dtype=float)
    bm = _minmax(bm_raw); rows=[]
    for i, paper in enumerate(papers):
        prior = paper_quality_prior(paper)
        combined = float(np.clip(bm[i] + prior, 0, 1))
        rows.append({**paper, "bm25_score":float(bm_raw[i]), "bm25_score_norm":float(bm[i]),
                     "semantic_similarity_norm":None, "quality_prior":prior,
                     "hybrid_score":combined, "ranking_mode":"bm25_api_only"})
    return pd.DataFrame(rows).sort_values("hybrid_score", ascending=False).head(top_n).reset_index(drop=True)
