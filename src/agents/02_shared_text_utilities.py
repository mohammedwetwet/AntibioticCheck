EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent":"ABX-AI-research-prototype/4.0 educational use"})
STOPWORDS = set("a an the is are was were be been being do does did not no and or to of for in on with as by it this that these those can could may might should would will how what why from into about after before between than then their them they there which while".split())

def clean_text(value):
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def tokenize(text):
    return re.findall(r"[a-z0-9]+", clean_text(text).lower())

def source_identifier(record):
    for key, prefix in [("pmid","PMID:"),("pmcid","PMCID:"),("doi","DOI:")]:
        value = str(record.get(key) or "").strip()
        if value:
            return prefix + value.lower()
    title = re.sub(r"[^a-z0-9]+"," ",clean_text(record.get("title","")).lower()).strip()
    return "TITLE:" + hashlib.sha1(title.encode()).hexdigest()[:12] if title else ""

def source_url(record):
    if record.get("pmid"): return "https://pubmed.ncbi.nlm.nih.gov/" + str(record["pmid"]) + "/"
    if record.get("pmcid"): return "https://europepmc.org/articles/" + str(record["pmcid"])
    if record.get("doi"): return "https://doi.org/" + str(record["doi"])
    return ""

def year_from_record(record):
    raw = str(record.get("firstPublicationDate") or record.get("pubYear") or "")
    match = re.search(r"\b(?:19|20)\d{2}\b", raw)
    return match.group(0) if match else ""
