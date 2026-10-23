# AntibioticCheck — Gemma 4 API Edition

A research prototype for evaluating public claims about antibiotics against biomedical literature. Adapted from the uploaded ABX-AI v9 notebook. The project preserves its main workflow (scope/safety, query planning, Europe PMC retrieval, ranking, passage extraction, NLI stance, citation/context audit, conservative reporting, human review, and benchmark helpers) while replacing local model inference with hosted Google Gemma 4.

## Model and downloads

- **Inference model:** `gemma-4-26b-a4b-it` through Google GenAI (`google-genai`).
- **Local transformer NLI:** removed.
- **Local sentence-transformer embeddings:** removed; ranking uses BM25 + a transparent metadata prior.
- No model weights are downloaded at startup. Python packages still need to be installed once.
- Network is required for Google GenAI calls and Europe PMC retrieval. API limits/charges depend on your account.

Official Gemma API docs: https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api

## Get a Google API key

1. Open Google AI Studio: https://aistudio.google.com/app/apikey
2. Create or copy your API key.
3. Paste it into the password field in the app, or set `GOOGLE_API_KEY` in your environment.
4. Never share the key or commit it to GitHub.

## Run on Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

## Run the notebook

Open `notebooks/AntibioticCheck_MultiAgent_Gemma4.ipynb` in Jupyter or Kaggle. Run the setup cell, enter the key when prompted, then run cells in order. The benchmark is disabled by default to avoid unexpected API calls.

## Architecture

`src/agents/` contains separate, inspectable modules for each agent, loaded into a shared namespace by `src/pipeline.py` to preserve the original notebook's dependency flow. The notebook is also organized into separate sections per agent. The project is inspired by the multi-agent scientific claim verification design in [MASCV](https://github.com/Beshoy-Zaki/Multi-Agent-Scientific-Claim-Verification-System), but this is not a full reimplementation of that repository.

## Important limitations

- Research prototype only; not diagnosis or treatment advice.
- Gemma output is not ground truth; model confidence is not a calibrated probability.
- Europe PMC retrieval can miss papers and abstracts can omit important context.
- Metadata does not prove that a cited paper supports a passage. Review full studies.
- The original starter benchmark is not expert-adjudicated.
- API integration and live Europe PMC workflow must be tested with your own API key and network. Syntax checks do not establish scientific validity.
