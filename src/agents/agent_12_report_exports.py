def json_default(value):
    if isinstance(value,(np.integer,)): return int(value)
    if isinstance(value,(np.floating,)): return float(value)
    if isinstance(value,(np.bool_,)): return bool(value)
    if isinstance(value,(np.ndarray,)): return value.tolist()
    if isinstance(value,(pd.Timestamp,)): return value.isoformat()
    if pd.isna(value) if not isinstance(value,(dict,list,tuple,set)) else False: return None
    return str(value)
def write_json(path,obj):
    with open(path,"w",encoding="utf-8") as f: json.dump(obj,f,indent=2,ensure_ascii=False,default=json_default)

def create_pdf_report(output,path):
    styles=getSampleStyleSheet()
    doc=SimpleDocTemplate(str(path),pagesize=letter,rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=40)
    story=[]; result=output["result"]
    story += [Paragraph("PublicHealth Evidence AI — Preliminary Claim Report",styles["Title"]),Spacer(1,10)]
    for label,value in [("Claim ID",output.get("claim_id","")),("Claim",output.get("claim","")),
                        ("Provisional status",result.get("verdict","")),("Reason",result.get("reason","")),
                        ("Sources retrieved",result.get("sources_retrieved",0)),("Candidate passages",result.get("candidate_passages",0))]:
        story.append(Paragraph(f"<b>{escape(str(label))}:</b> {escape(str(value))}",styles["BodyText"]))
    story += [Spacer(1,10),Paragraph("Candidate evidence (requires human review)",styles["Heading2"])]
    evidence=output.get("evidence_analysis",pd.DataFrame())
    if evidence.empty: story.append(Paragraph("No candidate passages retained. This does not prove that no evidence exists.",styles["BodyText"]))
    else:
        for i,(_,r) in enumerate(evidence.iterrows(),start=1):
            story.append(Paragraph(f"{i}. <b>{escape(str(r.get('title','Untitled')))}</b> ({escape(str(r.get('source_id','')) )})",styles["BodyText"]))
            story.append(Paragraph("NLI signal: "+escape(str(r.get("nli_label","unknown")))+" | Context flags: "+escape(str(r.get("context_flags","") or "none")),styles["BodyText"]))
            story.append(Paragraph("Candidate passage: "+escape(str(r.get("candidate_sentence",""))),styles["BodyText"]))
            if r.get("url"): story.append(Paragraph("Source: "+escape(str(r.get("url",""))),styles["BodyText"]))
            story.append(Spacer(1,7))
    story += [Spacer(1,8),Paragraph("Synthesis",styles["Heading2"]),
              Paragraph(escape(str(result.get("synthesis",""))).replace("\n","<br/>"),styles["BodyText"]),
              Spacer(1,8),Paragraph("Limitations",styles["Heading2"])]
    for item in result.get("limitations",[]): story.append(Paragraph("• "+escape(str(item)),styles["BodyText"]))
    story.append(Paragraph(escape(str(result.get("disclaimer","Research prototype only."))),styles["Italic"]))
    doc.build(story); return path
