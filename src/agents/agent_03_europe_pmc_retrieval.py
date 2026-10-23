def europe_pmc_search(query, page_size=MAX_RESULTS_PER_QUERY):
    response = SESSION.get(EUROPE_PMC_URL, params={
        "query": query, "format": "json", "pageSize": int(page_size), "resultType": "core"
    }, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json().get("resultList", {}).get("result", []) or []

def normalize_record(item):
    pubtypes = item.get("pubTypeList", {}).get("pubType", []) or []
    if isinstance(pubtypes, str):
        pubtypes = [pubtypes]
    rec = {
        "title": clean_text(item.get("title", "")),
        "abstract": clean_text(item.get("abstractText", "")),
        "year": year_from_record(item),
        "publication_date": str(item.get("firstPublicationDate") or ""),
        "journal": clean_text(item.get("journalTitle", "")),
        "authors": clean_text(item.get("authorString", "")),
        "publication_types": "; ".join(clean_text(x) for x in pubtypes if x),
        "is_open_access": str(item.get("isOpenAccess") or ""),
        "pmid": str(item.get("pmid") or "").strip(),
        "pmcid": str(item.get("pmcid") or "").strip(),
        "doi": str(item.get("doi") or "").strip()
    }
    rec["source_id"] = source_identifier(rec)
    rec["url"] = source_url(rec)
    return rec

def research_retriever_agent(queries):
    start = time.time()
    records, query_logs = [], []
    for query in queries:
        q_start = time.time()
        try:
            raw = europe_pmc_search(query)
            records.extend([normalize_record(x) for x in raw if x.get("title") or x.get("abstractText")])
            query_logs.append({"query": query, "status": "success", "raw_count": len(raw),
                               "elapsed_seconds": round(time.time()-q_start, 3), "error": ""})
        except Exception as exc:
            query_logs.append({"query": query, "status": "error", "raw_count": 0,
                               "elapsed_seconds": round(time.time()-q_start, 3), "error": str(exc)[:400]})
    unique, seen_ids, seen_titles = [], set(), set()
    for rec in records:
        sid = rec.get("source_id", "")
        title = re.sub(r"[^a-z0-9]+", " ", rec.get("title", "").lower()).strip()
        if sid and sid in seen_ids:
            continue
        if title and title in seen_titles:
            continue
        duplicate = False
        for old in unique:
            old_title = re.sub(r"[^a-z0-9]+", " ", old.get("title", "").lower()).strip()
            if title and old_title and SequenceMatcher(None, title, old_title).ratio() >= 0.93:
                duplicate = True
                break
        if duplicate:
            continue
        unique.append(rec)
        if sid: seen_ids.add(sid)
        if title: seen_titles.add(title)
    statuses = [x["status"] for x in query_logs]
    status = "success" if unique and "success" in statuses else ("empty" if "success" in statuses else "error")
    return {"status": status, "papers": unique, "retrieved_count": len(unique), "query_logs": query_logs,
            "elapsed_seconds": round(time.time()-start, 3),
            "error": "; ".join(x["error"] for x in query_logs if x["error"])}
