import os, sys, json, time, html
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from pipeline import load_pipeline

st.set_page_config(page_title="AntibioticCheck | Scientific Evidence", page_icon="🧬", layout="wide")
st.markdown("""<style>
:root{color-scheme:dark}
.stApp{background:linear-gradient(135deg,#07111f 0%,#0b1728 55%,#0a1e2b 100%);color:#e8f0f7}
[data-testid="stSidebar"]{background:#091523;border-right:1px solid #1d344a}
.block-container{padding-top:2.4rem;padding-bottom:2rem;max-width:1320px}
.ac-kicker{color:#42e8d4;font-size:.76rem;letter-spacing:.17em;font-weight:800;text-transform:uppercase}
.ac-brand{text-align:center;padding:1rem 0 .75rem;margin:0 auto .65rem;max-width:900px}
.ac-brand-mark{display:inline-flex;align-items:center;justify-content:center;width:48px;height:48px;border-radius:15px;background:linear-gradient(135deg,#00b8d9,#22d6bf);color:#061421;font-size:1.45rem;font-weight:900;box-shadow:0 8px 24px rgba(0,210,200,.15);margin-bottom:.45rem}
.ac-brand-mark span{font-size:.8rem;align-self:flex-start;margin-top:7px}
.ac-brand-name{font-size:1.3rem;font-weight:850;letter-spacing:-.025em;color:#f4f8fc;margin-bottom:.45rem}
.ac-title{text-align:center;font-size:2.35rem;font-weight:850;letter-spacing:-.04em;margin:.15rem 0 .45rem;color:#f4f8fc}
.ac-sub{text-align:center;color:#a9bdd0;font-size:1.02rem;margin:0 auto 1.45rem;max-width:800px;line-height:1.65}
.ac-card{background:linear-gradient(145deg,rgba(20,43,66,.94),rgba(10,27,43,.94));border:1px solid #28445c;border-radius:18px;padding:1.2rem 1.4rem;margin:.6rem 0}
.ac-warn{background:#332a22;border-left:5px solid #f7b955;border-radius:12px;padding:1rem 1.2rem;color:#ffe4b2;margin:1rem 0}
.ac-info{background:#102c40;border-left:5px solid #31c8d7;border-radius:12px;padding:1rem 1.2rem;color:#d8f4fb;margin:1rem 0}
.ac-footer{border-top:1px solid #28445c;margin-top:2.5rem;padding:1.5rem .25rem .5rem;color:#a9bdd0;font-size:.93rem;text-align:center}
.ac-footer a{color:#42e8d4;text-decoration:none;font-weight:700}
.ac-socials{display:flex;justify-content:center;align-items:center;gap:12px;margin:1rem 0 .9rem;flex-wrap:wrap}
.ac-social{display:inline-flex;align-items:center;gap:8px;padding:9px 13px;border:1px solid #31516a;border-radius:12px;background:#10263b;color:#dceaf5!important;font-weight:700;text-decoration:none!important;transition:all .18s ease}
.ac-social:hover{border-color:#42e8d4;background:#15364b;transform:translateY(-1px)}
.ac-social svg{width:19px;height:19px;display:block;fill:currentColor}
div.stButton>button[kind="primary"]{background:linear-gradient(90deg,#00b8d9,#22d6bf);color:#061421;border:0;font-weight:800;border-radius:12px;min-height:3.15rem;box-shadow:0 8px 22px rgba(0,205,195,.12);transition:transform .15s ease,filter .15s ease}div.stButton>button[kind="primary"]:hover{filter:brightness(1.06);transform:translateY(-1px)}
[data-testid="stMetric"]{background:#10263b;border:1px solid #29465e;padding:1rem;border-radius:14px}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🧬 AntibioticCheck")
    st.caption("A research tool for checking claims about antibiotics")
    api_key = st.text_input(
        "Google API key", type="password",
        help="Used by this running session. Do not share it or commit it to a repository."
    )
    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown(
        "1. **Understand the claim** — identify what needs checking.\n\n"
        "2. **Find scientific papers** — search biomedical research sources.\n\n"
        "3. **Review the evidence** — select relevant passages and compare them with the claim.\n\n"
        "4. **Show a preliminary result** — summarize what the retrieved research appears to say."
    )
    show_trace = st.checkbox("Show technical process details", value=False)

st.markdown(
    '<div class="ac-brand">'
    '<div class="ac-brand-mark">A<span>+</span></div>'
    '<div class="ac-brand-name">AntibioticCheck</div>'
    '<div class="ac-kicker">SCIENTIFIC EVIDENCE · ANTIBIOTIC CLAIMS</div>'
    '</div>',
    unsafe_allow_html=True
)
st.markdown('<div class="ac-title">What does the research say?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="ac-sub">Check a public claim against evidence found in scientific research papers.</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="ac-warn"><b>Important health information:</b> This app can make mistakes and its results are not guaranteed to be 100% accurate. It is a research prototype, not medical advice. Always consult a qualified doctor, pharmacist, or relevant researcher before relying on a result. Never use it to diagnose, choose, start, or stop a treatment.</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="ac-info"><b>Where do results come from?</b> Each assessment is based on scientific papers and selected evidence passages retrieved during the search. The AI compares those passages with the claim; it does not replace reading the original papers or expert review.</div>',
    unsafe_allow_html=True
)

claim = st.text_area(
    "Claim to investigate",
    value="",
    height=100,
    placeholder="Enter Public Claim about Antibiotics"
)
button_left, button_center, button_right = st.columns([1, 2.2, 1])
with button_center:
    run = st.button("Review scientific evidence", type="primary", use_container_width=True)

if run:
    if not api_key.strip():
        st.error("Enter your Google API key in the sidebar first.")
    elif not claim.strip():
        st.error("Enter a claim first.")
    else:
        with st.spinner("Searching scientific papers and reviewing selected evidence…"):
            try:
                ns = load_pipeline(api_key=api_key)
                ns["LLM_ENABLED"] = True
                start = time.time()
                output = ns["supervisor_agent"]("USER-CLAIM", claim.strip(), print_steps=False)
                output["elapsed_seconds"] = round(time.time() - start, 2)
                st.session_state["abx_last_output"] = output
            except Exception as exc:
                st.error("The review could not be completed. Please try again. If the problem continues, check the app logs.")
                if show_trace:
                    st.exception(exc)

if "abx_last_output" in st.session_state:
    output = st.session_state["abx_last_output"]
    result = output.get("result", {})
    direction = str(result.get("provisional_direction", "insufficient_evidence"))
    verdict_map = {
        "supports_claim": "Supported",
        "context_dependent": "Partially Supported",
        "contradicts_claim": "Unsupported",
        "insufficient_evidence": "Inconclusive",
        "mixed_or_conflicting": "Inconclusive",
        "technical_failure": "Inconclusive",
        "not_assessed": "Inconclusive",
    }
    raw_explanation = str(result.get("direct_answer", result.get("verdict", "")))
    result["verdict_explanation"] = raw_explanation
    result["verdict"] = verdict_map.get(direction, "Inconclusive")
    result["direct_answer"] = result["verdict"]

    st.markdown("## Assessment report")
    m1, m2, m3 = st.columns(3)
    m1.metric("Research papers found", output.get("retrieval", {}).get("retrieved_count", 0))
    m2.metric("Review stage", "Preliminary AI review")
    m3.metric("Time taken", f"{output.get('elapsed_seconds', 0):.1f} s")

    st.markdown(
        f'<div class="ac-card"><div class="ac-kicker">Preliminary evidence assessment</div>'
        f'<h2>{html.escape(str(result.get("verdict", "Inconclusive")))}</h2>'
        f'<p>{html.escape(str(result.get("reason", "")))}</p></div>',
        unsafe_allow_html=True
    )

    t1, t2, t3, t4 = st.tabs(["Summary", "Evidence passages", "Scientific papers", "Process details"])
    with t1:
        st.subheader("What the research suggests")
        synthesis = result.get("synthesis", output.get("synthesis", {}).get("summary", "No summary was generated."))
        st.write(synthesis)
        st.info(
            "This result is based on the papers and passages retrieved for this search. Search results may be incomplete, "
            "and abstracts may leave out important details. Please check the original research and consult a qualified expert."
        )
    with t2:
        df = output.get("evidence_analysis", pd.DataFrame())
        if df is None or df.empty:
            st.warning("No relevant evidence passages were retained. This does not mean that no scientific evidence exists.")
        else:
            preferred = [c for c in ["source_id", "title", "year", "nli_label", "nli_confidence", "context_flags", "candidate_sentence", "url"] if c in df.columns]
            st.dataframe(df[preferred], use_container_width=True, hide_index=True)
            st.download_button("Download evidence CSV", df.to_csv(index=False).encode(), "evidence_review.csv", "text/csv")
    with t3:
        papers = output.get("ranked_papers", pd.DataFrame())
        if papers is None or papers.empty:
            st.warning("No papers were retrieved for this search.")
        else:
            paper_cols = [c for c in ["source_id", "title", "year", "journal", "publication_types", "hybrid_score", "url"] if c in papers.columns]
            st.dataframe(papers[paper_cols], use_container_width=True, hide_index=True)
            st.download_button("Download paper list CSV", papers.to_csv(index=False).encode(), "retrieved_papers.csv", "text/csv")
    with t4:
        if show_trace:
            st.json(output.get("trace", []))
        else:
            st.caption("Turn on ‘Show technical process details’ in the sidebar to view the agent steps.")

    report = {
        "claim": output.get("claim"),
        "result": result,
        "trace": output.get("trace", []),
        "retrieval_status": output.get("retrieval", {}).get("status"),
        "sources_retrieved": output.get("retrieval", {}).get("retrieved_count", 0),
    }
    st.download_button(
        "Download assessment report (JSON)",
        json.dumps(report, ensure_ascii=False, indent=2, default=str).encode(),
        "antibioticcheck_report.json",
        "application/json"
    )

st.markdown(
    '<div class="ac-footer">'
    '<b>AntibioticCheck</b><br>'
    'A student research prototype · Assessments are based on scientific papers and may be incomplete or incorrect. '
    'Always review the original research and consult a qualified professional.'
    '<div class="ac-socials">'
    '<a class="ac-social" href="https://www.linkedin.com/in/mohammed-adel-ai-ml-dl/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">'
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.85 0-2.13 1.44-2.13 2.94v5.67H9.35V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.26 2.37 4.26 5.45v6.29zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.44c.98 0 1.79-.77 1.79-1.72V1.72C24 .77 23.2 0 22.22 0z"/></svg>LinkedIn</a>'
    '<a class="ac-social" href="https://www.instagram.com/_5fdw?cplk=MW01M3k1MGxxNmVpMw==" target="_blank" rel="noopener noreferrer" aria-label="Instagram">'
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.8 2h8.4A5.8 5.8 0 0 1 22 7.8v8.4a5.8 5.8 0 0 1-5.8 5.8H7.8A5.8 5.8 0 0 1 2 16.2V7.8A5.8 5.8 0 0 1 7.8 2zm0 2A3.8 3.8 0 0 0 4 7.8v8.4A3.8 3.8 0 0 0 7.8 20h8.4a3.8 3.8 0 0 0 3.8-3.8V7.8A3.8 3.8 0 0 0 16.2 4H7.8zM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6zm5.2-3.5a1.2 1.2 0 1 1 0 2.4 1.2 1.2 0 0 1 0-2.4z"/></svg>Instagram</a>'
    '<a class="ac-social" href="https://wa.me/201550428605" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp">'
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.52 3.48A11.82 11.82 0 0 0 12.1 0C5.53 0 .18 5.35.18 11.92c0 2.1.55 4.15 1.6 5.96L.08 24l6.27-1.64a11.9 11.9 0 0 0 5.74 1.46h.01c6.57 0 11.92-5.35 11.92-11.92 0-3.18-1.24-6.17-3.5-8.42zM12.1 21.8h-.01a9.9 9.9 0 0 1-5.04-1.38l-.36-.21-3.72.98.99-3.63-.24-.37a9.87 9.87 0 0 1-1.52-5.27c0-5.46 4.44-9.9 9.91-9.9a9.83 9.83 0 0 1 7.01 2.91 9.83 9.83 0 0 1 2.9 7.01c0 5.46-4.44 9.9-9.91 9.9zm5.43-7.41c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.47-.89-.8-1.49-1.78-1.66-2.08-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.49s1.07 2.89 1.22 3.09c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.5 1.69.64.71.23 1.36.2 1.87.12.57-.08 1.76-.72 2.01-1.42.25-.7.25-1.3.17-1.42-.07-.13-.27-.2-.57-.35z"/></svg>WhatsApp</a>'
    '<a class="ac-social" href="https://github.com/mohammedwetwet" target="_blank" rel="noopener noreferrer" aria-label="GitHub">'
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .9a11.1 11.1 0 0 0-3.51 21.63c.55.1.76-.24.76-.54v-2.1c-3.1.67-3.76-1.32-3.76-1.32-.5-1.28-1.23-1.62-1.23-1.62-1.01-.69.08-.68.08-.68 1.12.08 1.71 1.15 1.71 1.15.99 1.7 2.6 1.21 3.23.92.1-.72.39-1.21.71-1.49-2.48-.28-5.09-1.24-5.09-5.52 0-1.22.44-2.22 1.15-3-.12-.28-.5-1.42.11-2.96 0 0 .94-.3 3.05 1.15a10.6 10.6 0 0 1 5.55 0c2.11-1.45 3.05-1.15 3.05-1.15.61 1.54.23 2.68.11 2.96.72.78 1.15 1.78 1.15 3 0 4.29-2.61 5.23-5.1 5.51.4.35.76 1.03.76 2.08v3.07c0 .3.2.65.77.54A11.1 11.1 0 0 0 12 .9z"/></svg>GitHub</a>'
    '</div>'
    'Developed by <b>Mohamed (Adel) Wetwet</b>'
    '</div>',
    unsafe_allow_html=True
)
