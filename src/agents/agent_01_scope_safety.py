PERSONAL_PATTERNS = [
 r"\bwhat dose\b", r"\bwhich antibiotic should i\b", r"\bshould i take\b",
 r"\bcan i take\b", r"\bwhat medicine should\b", r"\bmy symptoms\b",
 r"\bdiagnose me\b", r"\bfor my infection\b"
]
def scope_safety_agent(claim):
    text = clean_text(claim)
    if len(text) < 8 or len(text) > 1000:
        return {"allowed":False,"status":"invalid_input","reason":"Please provide a complete public claim under 1000 characters."}
    if any(re.search(p,text.lower()) for p in PERSONAL_PATTERNS):
        return {"allowed":False,"status":"personal_medical_request_blocked","reason":"This system checks public claims and cannot provide personal diagnosis or treatment advice."}
    return {"allowed":True,"status":"allowed_public_claim","reason":"Passed basic public-claim scope rules."}
