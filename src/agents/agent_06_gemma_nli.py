NLI_LOAD_ERROR = ""
def canonical_nli_label(label):
    label = str(label).lower()
    if "entail" in label or "support" in label: return "entailment"
    if "contrad" in label or "refute" in label: return "contradiction"
    if "neutral" in label or "unclear" in label: return "neutral"
    return "unknown"

def _extract_json_object(text):
    text = str(text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match: raise ValueError("Gemma response did not contain a JSON object.")
    return json.loads(match.group(0))

def check_nli(claim, sentence):
    """Hosted Gemma stance classification. Scores are model estimates, not calibrated truth probabilities."""
    try:
        client = get_genai_client()
        prompt = ("You are an evidence-stance classifier for a scientific literature research prototype.\n"
                  "Compare EVIDENCE PASSAGE (premise) with EXACT CLAIM (hypothesis). Return ONLY a JSON object with keys label (entailment, contradiction, or neutral), confidence (0 to 1, NOT a calibrated probability), and rationale.\n"
                  "Entailment only if the passage directly supports the exact claim; contradiction only if it directly conflicts; neutral if unrelated, indirect, reports prescribing/beliefs rather than efficacy, or lacks context. Preserve negation and distinguish bacterial from viral infections. Do not infer efficacy from prescribing frequency.\n"
                  + "EVIDENCE PASSAGE: " + str(sentence) + "\nEXACT CLAIM: " + str(claim))
        response = client.models.generate_content(model=NLI_MODEL_NAME, contents=prompt)
        obj = _extract_json_object(getattr(response, "text", ""))
        label = canonical_nli_label(obj.get("label", "unknown"))
        if label not in {"entailment", "contradiction", "neutral"}: raise ValueError("Gemma returned an unsupported label.")
        try: confidence = max(0.0, min(1.0, float(obj.get("confidence", 0.0))))
        except Exception: confidence = 0.0
        return {"nli_label":label, "nli_scores":{"model_confidence":confidence}, "nli_confidence":confidence,
                "nli_error":"", "nli_rationale":str(obj.get("rationale", ""))}
    except Exception as exc:
        return {"nli_label":"analysis_error", "nli_scores":{}, "nli_confidence":0.0,
                "nli_error":str(exc)[:500], "nli_rationale":""}

def _antibiotic_viral_direct_stance(claim, passage):
    """Conservative lexical guard for direct antibiotic/viral claims; avoids treating prescribing practice as efficacy."""
    c = re.sub(r"\s+", " ", str(claim).lower())
    p = re.sub(r"\s+", " ", str(passage).lower())
    claim_is_antibiotic_viral = bool(
        re.search(r"\b(antibiotic|antibiotics)\b", c)
        and re.search(r"\b(viral|viruses|virus|influenza|flu|common cold|colds)\b", c)
    )
    if not claim_is_antibiotic_viral:
        return None
    passage_has_antibiotic = bool(re.search(r"\b(antibiotic|antibiotics)\b", p))
    passage_has_target = bool(re.search(r"\b(viral|viruses|virus|influenza|flu|common cold|colds)\b", p))
    # If a passage does not address both the medicine class and the claim's viral target,
    # it cannot be counted as direct evidence for/against this specific claim.
    if not (passage_has_antibiotic and passage_has_target):
        return "neutral"
    # Prescribing frequency is not evidence of antiviral efficacy.
    prescribing_only = bool(re.search(r"\b(prescribed|prescription rate|prescribing|prescriptions)\b", p)
                            and not re.search(r"\b(do not|does not|don't|doesn't|not treat|not work|ineffective|should not|cannot)\b", p))
    if prescribing_only:
        return "neutral"
    # Passage must make an efficacy/treatment statement, not merely mention diagnostic difficulty.
    efficacy_pattern = r"\b(treat|treating|treatment|work against|effective against|recommended to treat|used to treat)\b"
    if not re.search(efficacy_pattern, p):
        return None
    claim_negative = bool(re.search(r"\b(do not|does not|don't|doesn't|cannot|never|not)\b", c))
    passage_negative = bool(re.search(r"\b(do not|does not|don't|doesn't|cannot|never|not|ineffective|should not)\b", p))
    # Positive claim + explicit negative evidence => contradiction; negative claim + explicit negative evidence => entailment.
    if claim_negative and passage_negative:
        return "entailment"
    if not claim_negative and passage_negative:
        return "contradiction"
    if claim_negative and not passage_negative:
        return "contradiction"
    return "entailment"

def nli_evidence_agent(claim, passages):
    if passages.empty: return passages.copy()
    rows=[]
    for _,row in passages.iterrows():
        item=row.to_dict()
        nli = check_nli(claim,item.get("candidate_sentence",""))
        override = _antibiotic_viral_direct_stance(claim,item.get("candidate_sentence",""))
        item.update(nli)
        item["nli_model_label"] = nli.get("nli_label","unknown")
        item["domain_stance_override"] = override or ""
        if override:
            item["nli_label"] = override
            # Use a conservative fixed decision weight for explicit lexical rules; never present it as a probability.
            item["decision_confidence"] = 0.82 if override in {"entailment","contradiction"} else 0.0
            item["stance_method"] = "domain_rule_guard_overrode_nli"
        else:
            item["decision_confidence"] = float(nli.get("nli_confidence",0.0) or 0.0)
            item["stance_method"] = "nli_model"
        rows.append(item)
    return pd.DataFrame(rows)
