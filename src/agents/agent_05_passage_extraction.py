BOILERPLATE_PATTERNS = [
    r"\bstatistical analysis was performed using\b", r"\bdata were analyzed using\b",
    r"\bIBM Corp\b", r"\bSPSS version\b", r"\bthe authors declare no conflict\b",
    r"\bno conflict of interest\b", r"\bwritten informed consent\b",
    r"\bapproved by the institutional review board\b"
]

def split_sentences(text):
    text = clean_text(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    out = []
    for sentence in parts:
        sentence = sentence.strip()
        if len(sentence) < 35 or len(sentence) > 900:
            continue
        if any(re.search(pattern, sentence, re.I) for pattern in BOILERPLATE_PATTERNS):
            continue
        out.append(sentence)
    return out

def context_flags(sentence):
    t = sentence.lower()
    flags = []
    if re.search(r"\b(respondents|participants|survey|questionnaire|believed|perceived|awareness|knowledge)\b", t):
        flags.append("survey_or_belief_context")
    if re.search(r"\b(may|might|could|possibly|associated with|in this study|suggests?)\b", t):
        flags.append("uncertainty_or_study_context")
    if re.search(r"\b(secondary bacterial|co-infection|coinfection|superinfection)\b", t):
        flags.append("secondary_infection_context")
    if re.search(r"\b(prescribing|prescribed|prescription|antibiotic use|stewardship)\b", t):
        flags.append("use_or_prescribing_context")
    if re.search(r"\b(in vitro|mouse model|mice|murine|cell line|animal model)\b", t):
        flags.append("preclinical_context")
    if re.search(r"\b(review|systematic review|meta-analysis|survey|case report|editorial|guideline)\b", t):
        flags.append("study_type_may_matter")
    return "|".join(flags)

def _claim_overlap(claim, sentence):
    claim_tokens = {t for t in tokenize(claim) if t not in STOPWORDS and len(t) > 2}
    sent_tokens = set(tokenize(sentence))
    if not claim_tokens:
        return 0.0
    return len(claim_tokens & sent_tokens) / len(claim_tokens)

def rank_candidate_passages(claim, ranked_papers, top_n=MAX_EVIDENCE_PASSAGES):
    if ranked_papers.empty:
        return pd.DataFrame()
    candidates = []
    for _, paper in ranked_papers.iterrows():
        for j, sentence in enumerate(split_sentences(paper.get("abstract", ""))):
            flags = context_flags(sentence)
            candidates.append({
                "claim": claim, "source_id": paper.get("source_id", ""),
                "title": paper.get("title", ""), "year": paper.get("year", ""),
                "journal": paper.get("journal", ""), "publication_types": paper.get("publication_types", ""),
                "pmid": paper.get("pmid", ""), "pmcid": paper.get("pmcid", ""),
                "doi": paper.get("doi", ""), "url": paper.get("url", ""),
                "candidate_sentence": sentence, "sentence_index": j,
                "paper_hybrid_score": float(paper.get("hybrid_score", 0)),
                "context_flags": flags, "claim_token_overlap": _claim_overlap(claim, sentence)
            })
    if not candidates:
        return pd.DataFrame()
    texts = [item["candidate_sentence"] for item in candidates]
    tokenized = [tokenize(item) for item in texts]
    query_tokens = [t for t in tokenize(claim) if t not in STOPWORDS]
    bm = np.zeros(len(texts))
    if any(tokenized) and query_tokens:
        bm = _minmax(np.asarray(BM25Okapi(tokenized).get_scores(query_tokens), dtype=float))
    # API-only edition: deliberately use BM25 and claim overlap only.
    # No embedding_model object is created or downloaded in this project.
    sem = np.zeros(len(texts), dtype=float)
    sem_used = False
    rows = []
    for i, item in enumerate(candidates):
        overlap = item["claim_token_overlap"]
        semantic_score = sem[i] if sem_used else 0.0
        if sem_used:
            score = .30 * bm[i] + .35 * semantic_score + .20 * item["paper_hybrid_score"] + .15 * overlap
        else:
            score = .55 * bm[i] + .25 * item["paper_hybrid_score"] + .20 * overlap
        flags = item["context_flags"]
        if "survey_or_belief_context" in flags: score *= 0.70
        if "preclinical_context" in flags: score *= 0.80
        if "secondary_infection_context" in flags: score *= 0.80
        # Broad generic statements are retained in the audit but rank lower.
        if overlap < 0.15: score *= 0.65
        rows.append({
            **item, "sentence_bm25_norm": float(bm[i]),
            "sentence_semantic_similarity_norm": float(semantic_score),
            "passage_hybrid_score": float(max(0.0, score)), "semantic_used": sem_used
        })
    rows.sort(key=lambda item: item["passage_hybrid_score"], reverse=True)
    chosen, counts = [], {}
    for row in rows:
        sid = row["source_id"]
        # One passage per paper by default prevents one paper dominating the final stance.
        if counts.get(sid, 0) >= 1:
            continue
        chosen.append(row)
        counts[sid] = 1
        if len(chosen) >= top_n:
            break
    return pd.DataFrame(chosen)
