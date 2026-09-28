# ⚖️ LegalLens AI

### Understand contracts. Surface risks. Simplify the fine print.

LegalLens AI is an AI-powered contract analysis and simplification application built with **Python, Streamlit, and Groq-powered LLM inference**. It helps users explore the contents of an uploaded PDF contract through a structured analysis dashboard and a document-grounded conversational assistant.

The application extracts text from PDF pages, generates an overview of the agreement, and organizes model-generated insights into areas such as contract health, risks, fine-print alerts, fairness, missing clauses, and a before-you-sign checklist.

> **Note:** LegalLens AI is an informational aid. Its outputs are AI-generated and should be reviewed carefully; they are not a substitute for advice from a qualified legal professional.

---

## ✨ What it can do

| Capability | What it provides |
|---|---|
| 📄 **PDF text extraction** | Extracts readable text from uploaded PDF documents and retains page markers for reference. |
| 📊 **Contract health score** | Produces an indicative score from 0–100, with a classification and category-level breakdown. |
| ⚠️ **Risk analysis** | Highlights potential risks with severity, explanation, suggested action, and page reference where available. |
| 🚩 **Fine-print alerts** | Surfaces terms that may deserve closer attention, such as auto-renewal, hidden costs, or one-sided obligations when present in the document. |
| ⚖️ **Fairness analysis** | Provides an AI-generated view of whether terms appear to favor the client, vendor, or neither. |
| 🔍 **Missing-clause review** | Flags commonly relevant clauses that may not be present in the document. |
| 📋 **Before-you-sign checklist** | Creates a checklist of points to review before making a decision. |
| 💬 **Document-grounded AI chat** | Lets users ask questions about the uploaded document, with answers instructed to use the document text and cite page markers. |
| 🧑‍💼 **Role-aware explanations** | Supports different user personas, helping prioritize information relevant to a selected role. |
| 🗣️ **Simplified explanations** | Offers an “Explain Like I’m 15” style using everyday language and simple analogies. |

## 🔎 How it works

```text
Upload a contract PDF
        ↓
Extract text with page markers
        ↓
Send document context to an LLM
        ↓
Generate structured analysis
        ↓
Explore dashboard insights
        ↓
Ask follow-up questions in AI chat
```

1. **Upload:** The user provides a contract or agreement in PDF format.
2. **Extract:** PyPDF extracts available text from each page. Page markers are retained to support references.
3. **Analyze:** The application sends the extracted text to a Groq-hosted language model for structured analysis.
4. **Review:** The returned information is presented in dashboard tabs, including summary, health score, risks, fine print, fairness, checklist, and missing clauses.
5. **Ask:** Users can continue with document-focused questions through the interactive chat.

*Analysis quality depends on the text available in the PDF and the language model's output. Scanned or image-only PDFs may not yield extractable text without OCR.*

---

## 🧰 Tech stack

| Technology | Role |
|---|---|
| **Python** | Application logic and document-processing workflow |
| **Streamlit** | Interactive web interface and analysis dashboard |
| **Groq API** | Access to hosted LLM inference |
| **Large Language Models (LLMs)** | Document summarization, clause interpretation, and structured insight generation |
| **PyPDF** | PDF text extraction |
| **python-dotenv** | Loads configuration such as API keys from environment variables |

---

## 🚀 Run locally

### Prerequisites

- Python installed
- Git
- A Groq API key

### 1. Clone the repository

```bash
git clone https://github.com/Lavanya-star12/LegalLens-AI--Legal-Document-Simplifier.git
cd LegalLens-AI--Legal-Document-Simplifier
```

Replace `YOUR_REPOSITORY_URL` with the repository's clone URL. If your downloaded folder has a different name, use that folder name in the `cd` command.

### 2. Create and activate a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

** macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Keep this key private. Do not commit `.env` to version control. Ensure `.env` is listed in `.gitignore`.

### 5. Start the application

```bash
streamlit run app.py
```

Streamlit will display a local address in the terminal. Open it in your browser to use LegalLens AI.

---

## 📁 Project structure

```text
LegalLens-AI--Legal-Document-Simplifier/
├── app.py             # Streamlit application and analysis workflow
├── requirements.txt   # Python dependencies
├── .env               # Local secrets (create this; do not commit)
├── .gitignore         # Git ignore rules
├── screenshots/
│   └── dashboard.png  # Project dashboard screenshot
└── README.md          # Project documentation
```

---

## 🧪 Dependencies

The project currently lists these direct Python dependencies in `requirements.txt`:

- `streamlit`
- `python-dotenv`
- `groq`
- `pypdf`

---

## 🛣️ Potential next steps

- Add OCR support for scanned and image-based PDFs.
- Provide downloadable analysis reports.
- Add clause-level highlighting linked to PDF pages.
- Support side-by-side comparison of contract versions.
- Expand multilingual document explanations.
- Evaluate analysis quality using a curated set of sample contracts and human-reviewed results.

---

## 🤝 Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a branch for your change.
3. Make and test your update.
4. Commit your changes with a clear message.
5. Open a Pull Request describing what changed and why.

---

## ⚖️ Disclaimer

LegalLens AI is intended for **educational and informational purposes**. AI-generated summaries, risk indicators, fairness assessments, and suggested wording may be incomplete or inaccurate and should not be treated as legal advice or a legal opinion. The application does not establish whether a contract is legally valid or whether a user should sign it. Consult a qualified legal professional for advice about a specific situation.

---

<p align="center">
  <b>LegalLens AI</b><br>
  <i>Making complex legal language easier to understand.</i>
</p>
