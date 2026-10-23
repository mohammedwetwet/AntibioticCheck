from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parent / "agents"
MODULE_ORDER = [
    "00_config.py", "01_benchmark_claims.py", "02_shared_text_utilities.py",
    "agent_01_scope_safety.py", "agent_02_query_planning.py", "agent_03_europe_pmc_retrieval.py",
    "agent_04_hybrid_ranking.py", "agent_05_passage_extraction.py", "agent_06_gemma_nli.py",
    "agent_07_citation_context_audit.py", "agent_08_gemma_synthesis.py",
    "agent_09_decision_reporting.py", "agent_10_supervisor_orchestrator.py",
    "agent_11_review_packet.py", "agent_12_report_exports.py", "agent_13_benchmark.py",
    "agent_14_evaluation.py",
]

def load_pipeline(api_key=None):
    """Execute the split research-agent modules in one shared namespace, preserving notebook semantics."""
    import os
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key.strip()
        os.environ["GEMINI_API_KEY"] = api_key.strip()
    namespace = {"__name__": "abx_pipeline_runtime", "__file__": str(AGENTS_DIR / "00_config.py")}
    for filename in MODULE_ORDER:
        path = AGENTS_DIR / filename
        code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
        exec(code, namespace, namespace)
    return namespace
