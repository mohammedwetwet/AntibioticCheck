import argparse, json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from pipeline import load_pipeline
p=argparse.ArgumentParser(); p.add_argument("claim", help="Public antibiotic-related claim to investigate"); p.add_argument("--api-key", default=None); args=p.parse_args()
ns=load_pipeline(args.api_key); ns["LLM_ENABLED"]=True
out=ns["supervisor_agent"]("CLI-CLAIM", args.claim, print_steps=True)
print(json.dumps(out["result"], indent=2, ensure_ascii=False, default=str))
