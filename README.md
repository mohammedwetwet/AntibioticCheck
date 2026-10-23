# AntibioticCheck
### AI-Powered Scientific Evidence Review for Antibiotic-Related Claims

**AntibioticCheck** is an AI-powered research prototype designed to investigate public claims about antibiotics by retrieving scientific literature, analyzing relevant evidence passages, and generating a preliminary assessment of how the available evidence relates to a claim.

The project combines biomedical literature retrieval, relevance ranking, evidence extraction, and large language model (LLM)-based analysis to make scientific evidence easier to explore and understand.

> **Important:** AntibioticCheck is an experimental research prototype, not a medical device or clinical decision-support system. Its results may be incomplete or incorrect and must not be used to diagnose a condition, choose a treatment, or start or stop medication. Always consult a qualified healthcare professional for medical decisions.

---

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [Project Objectives](#project-objectives)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Assessment Categories](#assessment-categories)
- [Getting Started](#getting-started)
- [Running the Application](#running-the-application)
- [Understanding the Results](#understanding-the-results)
- [Limitations and Responsible Use](#limitations-and-responsible-use)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

---

## Overview

Antibiotics are essential medicines used to treat certain bacterial infections. However, public discussions about antibiotics often contain inaccurate, oversimplified, or misleading statements.

Evaluating these claims requires more than a simple web search. It involves finding relevant scientific publications, identifying the evidence they contain, understanding the context of the findings, and determining whether that evidence supports or contradicts the original statement.

AntibioticCheck explores how artificial intelligence can assist with this process.

A user submits a public claim about antibiotics. The system searches biomedical literature, ranks potentially relevant publications, extracts evidence passages, and uses a language model to compare the retrieved evidence with the claim.

The application then presents a preliminary assessment alongside a summary and the retrieved research materials, allowing users to investigate the underlying evidence rather than relying only on an AI-generated conclusion.

### Project Focus

- **Domain:** Artificial Intelligence, Biomedical Research, and Scientific Claim Verification
- **Primary Application:** Antibiotic-related public claims
- **Interface:** Streamlit web application
- **Literature Retrieval:** Europe PMC
- **Language Model:** Google Gemma 4 through an API
- **Primary Language:** Python

---

## The Problem

Scientific information about antibiotics is distributed across research papers, biomedical publications, and other scientific resources.

Several challenges make this information difficult to evaluate:

1. **Information overload:** Relevant scientific findings may be distributed across many publications.
2. **Retrieval challenges:** A search result may mention the same topic without directly addressing the claim being investigated.
3. **Evidence interpretation:** Scientific findings must be interpreted in context, including their scope and limitations.
4. **Oversimplification:** A broad public statement may be only partially supported by the available evidence.
5. **Uncertainty:** Retrieved literature may be insufficient, conflicting, or irrelevant to the exact claim.

AntibioticCheck investigates a structured AI-assisted workflow for organizing this process and presenting an accessible preliminary evidence assessment.

---

## Project Objectives

The project aims to:

- Investigate public claims about antibiotics using scientific literature.
- Retrieve potentially relevant biomedical publications.
- Rank search results according to their relevance to a submitted claim.
- Identify passages that may provide evidence for or against the claim.
- Use an LLM to analyze the relationship between the claim and the retrieved evidence.
- Produce a concise preliminary assessment with supporting context.
- Expose the retrieved publications and evidence passages so users can examine the underlying material.
- Represent uncertainty instead of forcing a definitive conclusion when the available evidence is insufficient.

The goal is to support scientific exploration, not to replace researchers, healthcare professionals, or systematic evidence reviews.

---

## Key Features

### 1. Claim-Based Investigation

Users can enter a public claim related to antibiotics and initiate an evidence review through a simple web interface.

### 2. Biomedical Literature Retrieval

The application searches scientific literature through Europe PMC to identify publications potentially relevant to the submitted claim.

### 3. Relevance Ranking

Retrieved material is ranked using BM25, a lexical information-retrieval method that helps identify documents relevant to the query.

### 4. Evidence Passage Analysis

The pipeline extracts and evaluates selected passages from retrieved scientific material rather than treating every search result as equally relevant.

### 5. LLM-Assisted Evidence Interpretation

Google Gemma 4 is used through an API to help analyze the relationship between the claim and the selected evidence.

### 6. Preliminary Verdict Generation

The application maps its internal assessment to one of four user-facing verdicts:

- Supported
- Partially Supported
- Unsupported
- Inconclusive

### 7. Evidence-Oriented Reporting

The Streamlit interface presents the assessment, a summary of what the retrieved research suggests, evidence passages, scientific publications, and additional process information.

### 8. Interactive Web Interface

Users can investigate a claim without manually running individual pipeline components.

### 9. Uncertainty-Aware Output

When the evidence is insufficient, mixed, conflicting, or the assessment cannot be completed reliably, the system can return an inconclusive result.

---

## How It Works

AntibioticCheck follows a multi-stage evidence review workflow.

### Step 1 — Submit a Claim

The user enters a public claim about antibiotics into the Streamlit interface.

Example:

`Antibiotics are effective against viral infections.`

This example illustrates the input format; it is not a predefined test result.

### Step 2 — Retrieve Scientific Literature

The system searches biomedical publications using Europe PMC and collects potentially relevant research material.

The retrieved publications form the starting point for the subsequent analysis.

### Step 3 — Rank Retrieved Material

The system uses BM25-based relevance ranking to prioritize publications or material that appears relevant to the submitted claim.

Relevance ranking helps narrow the search, but it does not establish whether a claim is scientifically correct.

### Step 4 — Extract Evidence Passages

Relevant passages are selected from the retrieved material for closer examination.

The purpose is to identify text that may directly support, qualify, or contradict the claim.

### Step 5 — Analyze the Evidence

Google Gemma 4 is used through an API to assist with interpreting the relationship between the claim and the selected evidence.

The analysis considers the available evidence and generates a preliminary assessment. The model's output is not independently guaranteed to be scientifically correct.

### Step 6 — Synthesize the Findings

The system organizes the analysis into a preliminary result and a summary of what the retrieved research appears to suggest.

### Step 7 — Present the Assessment

The Streamlit application presents the verdict and relevant research materials.

Users can inspect the evidence passages and scientific publications rather than treating the verdict as a standalone answer.

### Workflow Summary

**User Claim → Biomedical Literature Retrieval → BM25 Relevance Ranking → Evidence Passage Extraction → LLM-Assisted Analysis → Preliminary Assessment → Evidence-Oriented Report**

---

## System Architecture

The project separates the user interface from the research pipeline and its supporting agent modules.

### 1. User Interface

The Streamlit application provides the claim input, API-key input, preliminary assessment, and research report.

### 2. Pipeline Orchestration

The pipeline coordinates the stages required to process a claim and produce the final application output.

### 3. Literature Retrieval

The retrieval component searches biomedical literature and collects potentially relevant publications.

### 4. Evidence Processing

The evidence-processing components rank material, extract passages, and organize the selected evidence for analysis.

### 5. LLM-Assisted Analysis

Google Gemma 4 receives the relevant analysis context through an API and helps interpret the relationship between the claim and the retrieved material.

### 6. Assessment and Reporting

The assessment components organize the findings into a preliminary result and provide the information needed by the interface to display the report.

### Architecture Diagram

```text
                  USER
                   |
                   v
          Streamlit Web Interface
                   |
                   v
           Claim Processing
                   |
                   v
       Biomedical Literature Search
             (Europe PMC)
                   |
                   v
        Retrieved Research Material
                   |
                   v
        BM25 Relevance Ranking
                   |
                   v
        Evidence Passage Extraction
                   |
                   v
      Google Gemma 4 API Analysis
                   |
                   v
        Evidence-Based Synthesis
                   |
                   v
        Preliminary Assessment
                   |
                   v
       Report and Evidence Display
```

This diagram illustrates the conceptual workflow. Individual stages and their exact implementation details are defined by the project's source code.

---

## Technology Stack

| Technology | Role |
|---|---|
| Python | Core application and research pipeline |
| Streamlit | Interactive web interface |
| Europe PMC | Biomedical literature retrieval |
| BM25 | Lexical relevance ranking |
| Google Gemma 4 | LLM-assisted evidence analysis |
| Google API | Access to the language model |
| Pandas | Tabular evidence and report handling |

The project uses an API-based language model workflow rather than requiring locally downloaded Gemma model weights.

The exact dependency versions are specified in `requirements.txt`.

---

## Assessment Categories

AntibioticCheck presents one of four preliminary verdicts.

### Supported

The retrieved evidence appears to support the submitted claim.

This does not mean that every aspect of the claim has been conclusively established.

### Partially Supported

The evidence appears to support the claim only under certain conditions, within a limited scope, or with important qualifications.

### Unsupported

The retrieved evidence does not support the submitted claim and may contradict it.

This verdict does not automatically establish that the opposite statement is true.

### Inconclusive

The available retrieved evidence is insufficient, ambiguous, mixed, conflicting, or otherwise inadequate for a reliable preliminary assessment.

**Important distinction:** These verdicts describe the system's preliminary interpretation of the retrieved material. They are not formal clinical conclusions, and the completeness of the literature search is not guaranteed.

---

## Getting Started

Follow these steps to run the project locally.

### Prerequisites

You will need:

- Python installed on your computer.
- Git, if you want to clone the repository.
- Internet access for literature retrieval and API requests.
- A Google API key with access to the configured Gemma model.
- The project dependencies listed in `requirements.txt`.

### 1. Clone the Repository

```bash
git clone https://github.com/mohammedwetwet/AntibioticCheck.git
cd AntibioticCheck
```

If your local project folder has a different name, use that folder name instead.

### 2. Create a Virtual Environment

On Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use another terminal or configure your local PowerShell execution policy appropriately.

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Make sure `requirements.txt` exists in the repository root, then run:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the Google API Key

Start the application and provide your Google API key through the API-key input in the application sidebar.

**Security recommendations:**

- Never commit your API key to GitHub.
- Never place a real API key in the README.
- Do not share screenshots containing API keys.
- Keep credentials and local environment files out of version control.
- If a key is exposed publicly, revoke it and generate a replacement.

### 5. Run the Application

From the project root, run:

```bash
python -m streamlit run app.py
```

Streamlit will provide a local address for opening the application in your browser.

If your entry-point file has a different name in the current repository version, use the corresponding filename.

---

## Running an Assessment

1. Launch the application.
2. Provide your Google API key in the designated input.
3. Enter a public claim about antibiotics.
4. Select **Review scientific evidence**.
5. Wait for the application to retrieve publications and analyze the selected evidence.
6. Review the preliminary verdict and its explanation.
7. Examine the evidence passages and scientific papers.
8. Open the original publications to verify their context and findings.

### What Should You Examine?

When evaluating a result, consider:

- Does the publication directly address the submitted claim?
- Is the selected passage relevant to the claim?
- Does the passage support the entire claim or only part of it?
- Are there important qualifications or conflicting findings?
- Does the source provide enough context to interpret the finding?
- Is the evidence sufficient to justify the preliminary assessment?

A verdict should always be interpreted alongside its supporting material and limitations.

---

## Limitations and Responsible Use

AntibioticCheck is an experimental research prototype. Its output should be treated as a starting point for investigation, not as a final scientific judgment.

### 1. Incomplete Literature Retrieval

A search may miss relevant publications. Search coverage depends on the retrieval strategy, available indexing, and the material returned by the source.

### 2. Retrieval Does Not Guarantee Relevance

A publication may contain related terminology without directly answering the submitted claim.

### 3. LLM Hallucinations

Language models may produce inaccurate interpretations, omit qualifications, or draw conclusions that are not justified by the evidence.

### 4. Context Limitations

An extracted passage may not capture the full methodology, population, limitations, or conclusions of the original study.

### 5. Conflicting Scientific Evidence

Different studies may report different findings because of differences in study design, populations, methods, or research conditions.

### 6. No Guarantee of Scientific Completeness

The system does not guarantee a systematic review, exhaustive literature coverage, or expert-level verification of every claim.

### 7. Not for Clinical Decision-Making

The system must not be used to diagnose infections, select antibiotics, determine dosage, or decide whether to start or stop medication.

Medical decisions must be made with a qualified healthcare professional.

### Responsible Interpretation

Always inspect the original research and consult qualified experts when the accuracy or implications of a claim matter.

An inconclusive result should not be interpreted as evidence that no relevant scientific research exists.

---

## Future Improvements

Potential directions for future development include:

- Expanding the range of supported biomedical claim categories.
- Improving retrieval quality and coverage.
- Evaluating evidence-selection accuracy.
- Strengthening the connection between individual verdicts and their supporting passages.
- Improving handling of contradictory evidence.
- Adding systematic evaluation datasets and reproducible benchmarks.
- Measuring retrieval precision, evidence relevance, and verdict consistency.
- Improving uncertainty estimation and error analysis.
- Enhancing accessibility and multilingual support.
- Adding more comprehensive testing and reproducibility documentation.

These are potential improvements, not claims about functionality already implemented.

---

## Contributing

Contributions that improve retrieval quality, evidence traceability, evaluation, documentation, testing, and responsible AI use are welcome.

A useful contribution should:

1. Clearly describe the problem being addressed.
2. Explain the proposed change.
3. Include relevant tests when possible.
4. Avoid exposing API keys, credentials, or private information.
5. Distinguish measured results from assumptions or unverified claims.

For substantial changes, consider opening an issue before submitting a pull request.

---

## Acknowledgments

AntibioticCheck builds on the broader ecosystem of open scientific literature, information retrieval, Python development tools, and generative AI.

The project uses Europe PMC as a source of biomedical literature and Google Gemma 4 through an API for LLM-assisted analysis.

Please consult the relevant providers' documentation and terms when using their services.

---

## License

No license has been specified in this README.

Before distributing or reusing the project, choose and add an appropriate license file to the repository. Until a license is added, do not assume that the project is available for unrestricted reuse.
