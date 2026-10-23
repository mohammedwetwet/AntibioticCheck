def query_planning_agent(claim):
    """Generate complementary high-recall queries; each query has a distinct retrieval role."""
    claim_clean = clean_text(claim)
    tokens = [t for t in tokenize(claim_clean) if t not in STOPWORDS and len(t) > 2]
    # Keep meaningful claim terms, but avoid building a brittle query from every token.
    focus = list(dict.fromkeys(tokens))[:8]
    antibiotic_terms = '(antibiotic OR antibiotics OR antibacterial OR "antimicrobial agent")'
    queries = [
        # Core topic query: maximize recall in title/abstract.
        f'TITLE_ABS:{antibiotic_terms} AND TITLE_ABS:({" OR ".join(focus)})' if focus
        else f'TITLE_ABS:{antibiotic_terms}',
        # Claim-focused clinical terms.
        f'({antibiotic_terms}) AND TITLE_ABS:({" OR ".join(focus)})' if focus
        else f'{antibiotic_terms}',
        # Wider abstract/full-text indexed search catches papers with less specific titles.
        f'({antibiotic_terms}) AND ({" OR ".join(focus)})' if focus
        else antibiotic_terms,
    ]
    # Add claim phrase search where the text is short enough to be useful.
    if len(claim_clean.split()) <= 12:
        phrase = claim_clean.replace('"', '').strip()
        queries.append(f'TITLE_ABS:"{phrase}"')
    # For the common antibiotic/viral-infection topic, include a high-recall clinical variant.
    tset = set(tokens)
    if tset & {"virus", "viruses", "viral", "influenza", "flu", "cold"}:
        queries.extend([
            'TITLE_ABS:(antibiotic OR antibiotics) AND TITLE_ABS:(viral OR viruses OR influenza OR "common cold")',
            'TITLE_ABS:(antibiotic OR antibiotics) AND TITLE_ABS:(antiviral OR bacterial OR coinfection OR "secondary infection")'
        ])
    # Avoid malformed or duplicate strings; cap API calls to keep runtime bounded.
    return list(dict.fromkeys(q for q in queries if q))[:5]
