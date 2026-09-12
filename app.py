import json
import os
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader


# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="LegalLens AI — Legal Document Simplifier",
    page_icon="⚖️",
    layout="centered",
)


# ----------------------------
# Constants
# ----------------------------

SUGGESTED_QUESTIONS = [
    "Summarize this contract",
    "What are my responsibilities?",
    "Show payment terms",
    "Any legal risks?",
    "Find deadlines",
    "Explain confidentiality",
    "Who owns intellectual property?",
    "Should I sign this?",
]

RISK_DOT = {"low": "🟢", "medium": "🟡", "high": "🔴"}

HEALTH_LABEL = {
    "excellent": "🟢 Excellent",
    "safe": "🟢 Safe",
    "moderate risk": "🟡 Moderate Risk",
    "high risk": "🟠 High Risk",
    "critical risk": "🔴 Critical Risk",
}

CATEGORY_LABELS = {
    "payment_fairness": "💰 Payment Fairness",
    "liability": "🛡️ Liability",
    "confidentiality": "🔒 Confidentiality",
    "termination": "🚪 Termination",
    "renewal": "🔁 Renewal",
    "intellectual_property": "💡 Intellectual Property",
    "data_protection": "🗄️ Data Protection",
    "dispute_resolution": "⚖️ Dispute Resolution",
}

PERSONAS = [
    "None / General",
    "Student",
    "Freelancer",
    "Startup Founder",
    "Business Owner",
    "Tenant",
    "Landlord",
    "Employee",
    "Employer",
    "Investor",
    "HR",
    "Lawyer",
]


# ----------------------------
# Landing page styling
# ----------------------------

LANDING_CSS = """
<style>
.hero {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    padding: 2.75rem 2rem;
    border-radius: 16px;
    text-align: center;
    color: white;
    margin-bottom: 1.75rem;
}
.hero h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}
.hero p {
    font-size: 1.05rem;
    opacity: 0.9;
    max-width: 640px;
    margin: 0 auto;
}
.feature-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    height: 100%;
    margin-bottom: 0.9rem;
}
.feature-card h4 {
    margin: 0 0 0.3rem 0;
    font-size: 1rem;
}
.feature-card p {
    margin: 0;
    font-size: 0.85rem;
    color: #475569;
}
</style>
"""

FEATURES = [
    ("📊", "Contract Health Score", "0-100 score across payment, liability, confidentiality, IP and more."),
    ("⚠️", "Risk Analysis", "Every risky clause flagged with severity, reasoning and page reference."),
    ("🚩", "Fine Print Alerts", "Auto-renewals, hidden fees and one-sided clauses you might miss."),
    ("⚖️", "Fairness Analysis", "See who the contract favors — client, vendor, or balanced."),
    ("✍️", "Negotiation Suggestions", "Safer, ready-to-use wording for risky clauses."),
    ("🔍", "Missing Clause Detection", "Flags important protections the document leaves out."),
    ("📋", "Before-You-Sign Checklist", "A quick checklist to run through before signing."),
    ("💬", "Interactive Q&A", "Ask anything — answers are grounded only in your document."),
]


def render_landing_page():
    st.markdown(LANDING_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero">
            <h1>⚖️ LegalLens AI</h1>
            <p>Upload any contract or agreement and get an instant, plain-English
            breakdown — health score, risks, fine print, fairness, and a
            document-grounded chat assistant to answer your follow-up questions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    for idx, (icon, title, desc) in enumerate(FEATURES):
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div class="feature-card">
                    <h4>{icon} {title}</h4>
                    <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ----------------------------
# PDF extraction
# ----------------------------

@st.cache_data(show_spinner=False)
def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from uploaded PDF."""

    reader = PdfReader(BytesIO(pdf_bytes))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text:
            pages.append(f"[Page {page_number}]\n{text.strip()}")

    return "\n\n".join(pages)


# ----------------------------
# Prompts
# ----------------------------

def build_system_prompt(document_text: str, persona: str, eli15: bool) -> str:
    """Create the LegalLens AI system prompt covering the full feature set."""

    persona_instruction = (
        f'The user has identified their role as "{persona}". Prioritize information, '
        "risks, and responsibilities most relevant to that role."
        if persona and persona != "None / General"
        else "No specific persona was selected — give balanced, general-purpose answers."
    )

    eli15_instruction = (
        "The user has enabled 'Explain Like I'm 15' mode. Use everyday language, "
        "simple analogies, and avoid legal terminology entirely."
        if eli15
        else "Use clear plain English suitable for a non-lawyer, but you don't need to "
        "oversimplify with analogies unless asked."
    )

    return f"""
You are LegalLens AI, an intelligent Legal Contract Analysis Assistant.

Answer user questions ONLY using the contents of the uploaded document below.
Never invent legal information that is not explicitly stated. If information
is unavailable, respond exactly with:
"I couldn't find that information in the uploaded document."

The document text is prefixed with [Page N] markers — always cite the page
number(s) your answer is based on, e.g. "(Page 3)". Never make unsupported
claims.

CAPABILITIES — draw on these when relevant to the user's question:

1. Plain-English clause explanations, contract summaries, and party
   responsibilities.
2. Important dates, deadlines, renewal periods, and payment schedules.
3. Penalties, liabilities, and legal risks, including severity (Low/Medium/High).
4. Unusual or one-sided clauses, with suggested safer wording
   (show the original clause, then a suggested rewrite, then why it helps).
5. Missing clauses the document should probably have (confidentiality,
   termination, force majeure, arbitration, dispute resolution, data privacy,
   refund, payment, warranty, IP, liability, indemnity) and why that matters.
6. Fine print alerts: auto-renewal, non-refundable advances, long notice
   periods, one-sided obligations, high penalties, ownership transfers,
   hidden costs — explained simply.
7. Fairness analysis: who the contract favors and why.
8. "What if" simulations (e.g. "what happens if I pay late?") answered using
   only the uploaded contract, referencing the relevant clause.
9. A confidence label (High / Medium / Low) for non-trivial answers, based on
   whether the information is clearly stated, implied, or not found.
10. A "Should I sign this?" recommendation when asked
    (🟢 Safe to Sign / 🟡 Sign After Minor Changes / 🟠 Negotiate Before
    Signing / 🔴 Do Not Sign Yet) with reasoning.

PERSONA MODE: {persona_instruction}

EXPLANATION STYLE: {eli15_instruction}

FORMATTING: Organize longer answers with clear headings/bullets (e.g.
Summary, Responsibilities, Payment Terms, Deadlines, Risks, Missing Clauses,
Suggested Improvements) where it improves readability. Keep short factual
answers concise.

Never provide legal advice. When giving substantive analysis, end with:
"This explanation is for informational purposes and should not replace
professional legal advice."

Uploaded Legal Document:

{document_text}
""".strip()


def build_dashboard_prompt(document_text: str) -> str:
    """Ask the model for the full structured dashboard as JSON."""

    return f"""
You are a legal document analysis engine. Read the legal document below
(pages are marked with [Page N]) and return ONLY a single valid JSON object.
No markdown, no code fences, no commentary outside the JSON.

Return exactly this structure:

{{
  "document_type": string,
  "parties": [string],
  "duration": string,
  "contract_value": string,
  "important_dates": [string],
  "summary": string (2-4 sentences),

  "health_score": integer 0-100,
  "health_classification": one of "Excellent","Safe","Moderate Risk","High Risk","Critical Risk",
  "category_scores": {{
     "payment_fairness": {{"score": integer 0-100, "reason": string}},
     "liability": {{"score": integer 0-100, "reason": string}},
     "confidentiality": {{"score": integer 0-100, "reason": string}},
     "termination": {{"score": integer 0-100, "reason": string}},
     "renewal": {{"score": integer 0-100, "reason": string}},
     "intellectual_property": {{"score": integer 0-100, "reason": string}},
     "data_protection": {{"score": integer 0-100, "reason": string}},
     "dispute_resolution": {{"score": integer 0-100, "reason": string}}
  }},

  "risks": [
     {{"risk_name": string, "severity": "Low|Medium|High", "description": string,
       "page_number": string, "reason": string, "suggested_action": string}}
  ],

  "fine_print_alerts": [
     {{"title": string, "explanation": string}}
  ],

  "fairness": {{
     "client_friendly_percent": integer 0-100,
     "vendor_friendly_percent": integer 0-100,
     "balanced": "Yes|No",
     "explanation": string
  }},

  "contract_personality": {{"label": string, "emoji": string, "explanation": string}},

  "recommendation": {{
     "verdict": "Safe to Sign|Sign After Minor Changes|Negotiate Before Signing|Do Not Sign Yet",
     "explanation": string
  }},

  "missing_clauses": [
     {{"clause": string, "importance": string}}
  ],

  "before_you_sign_checklist": [string]
}}

Rules:
- Base everything strictly on the document text below. Do not invent facts.
- If a field cannot be determined, use "Not specified" (strings) or an empty
  array/list as appropriate.
- Cite page numbers in "page_number" using the [Page N] markers where possible.

Document:

{document_text}
""".strip()


def get_groq_client() -> Groq:
    """Return Groq client."""

    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not api_key:
        st.error(
            "GROQ_API_KEY is missing. Add it to the .env file and restart the application."
        )
        st.stop()

    return Groq(api_key=api_key)


def clear_chat():
    """Clear conversation."""

    st.session_state.messages = []


def generate_dashboard_data(client: Groq, model_name: str, document_text: str) -> dict:
    """Call Groq to produce the full structured dashboard, parsed as a dict."""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You output only valid JSON. Never include markdown, "
                    "code fences, or commentary.",
                },
                {"role": "user", "content": build_dashboard_prompt(document_text)},
            ],
            temperature=0,
            max_tokens=2500,
        )

        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.replace("json\n", "", 1).replace("json", "", 1)

        data = json.loads(raw)

    except Exception as exc:
        data = {"error": str(exc)}

    return data


# ----------------------------
# Dashboard rendering
# ----------------------------

def render_dashboard(data: dict):
    """Render the full One-Click Analysis Dashboard."""

    if "error" in data:
        st.warning(
            f"Couldn't generate the full analysis dashboard automatically. ({data['error']})"
        )
        return

    (
        tab_summary,
        tab_health,
        tab_risks,
        tab_fineprint,
        tab_fairness,
        tab_checklist,
        tab_missing,
    ) = st.tabs(
        [
            "📄 Summary",
            "📊 Health Score",
            "⚠️ Risks",
            "🚩 Fine Print",
            "⚖️ Fairness",
            "📋 Checklist",
            "🔍 Missing",
        ]
    )

    # --- Summary ---
    with tab_summary:
        with st.container(border=True):
            st.markdown("### 📄 Contract Summary")
            st.markdown("---")
            st.markdown(f"**📌 Document Type**\n\n{data.get('document_type', 'Not specified')}")
            st.markdown("**👥 Parties**")
            parties = data.get("parties") or []
            if parties:
                for p in parties:
                    st.markdown(f"{p}")
            else:
                st.markdown("Not specified")
            st.markdown(f"**📅 Duration**\n\n{data.get('duration', 'Not specified')}")
            st.markdown(f"**💰 Contract Value**\n\n{data.get('contract_value', 'Not specified')}")
            st.markdown("**📅 Important Dates**")
            dates = data.get("important_dates") or []
            if dates:
                for d in dates:
                    st.markdown(f"{d}")
            else:
                st.markdown("Not specified")
            if data.get("summary"):
                st.markdown("**📝 Summary**")
                st.markdown(data["summary"])

        personality = data.get("contract_personality") or {}
        recommendation = data.get("recommendation") or {}

        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("**🎭 Contract Personality**")
                st.markdown(f"{personality.get('emoji', '')} **{personality.get('label', 'Not specified')}**")
                st.caption(personality.get("explanation", ""))
        with col2:
            with st.container(border=True):
                verdict = recommendation.get("verdict", "Not specified")
                verdict_emoji = {
                    "Safe to Sign": "🟢",
                    "Sign After Minor Changes": "🟡",
                    "Negotiate Before Signing": "🟠",
                    "Do Not Sign Yet": "🔴",
                }.get(verdict, "⚪")
                st.markdown("**✅ Should I Sign This?**")
                st.markdown(f"{verdict_emoji} **{verdict}**")
                st.caption(recommendation.get("explanation", ""))

    # --- Health Score ---
    with tab_health:
        score = data.get("health_score", "N/A")
        classification = str(data.get("health_classification", "")).strip().lower()
        label = HEALTH_LABEL.get(classification, data.get("health_classification", "Not specified"))

        with st.container(border=True):
            st.markdown("### 📊 Contract Health Score")
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Overall Score", f"{score}/100" if isinstance(score, (int, float)) else score)
            with c2:
                st.markdown(f"**Classification:** {label}")
            if isinstance(score, (int, float)):
                st.progress(min(max(int(score), 0), 100) / 100)

        category_scores = data.get("category_scores") or {}
        if category_scores:
            st.markdown("#### Category Breakdown")
            for key, nice_label in CATEGORY_LABELS.items():
                entry = category_scores.get(key) or {}
                cat_score = entry.get("score", "N/A")
                with st.container(border=True):
                    cc1, cc2 = st.columns([1, 3])
                    with cc1:
                        st.markdown(f"**{nice_label}**")
                        st.markdown(f"{cat_score}/100" if isinstance(cat_score, (int, float)) else str(cat_score))
                    with cc2:
                        st.caption(entry.get("reason", "Not specified"))

    # --- Risks ---
    with tab_risks:
        risks = data.get("risks") or []
        st.markdown(f"### ⚠️ Risk Analysis ({len(risks)} found)")
        if not risks:
            st.info("No significant risks were identified in this document.")
        for risk in risks:
            severity = str(risk.get("severity", "")).strip().lower()
            dot = RISK_DOT.get(severity, "⚪")
            with st.expander(f"{dot} {risk.get('risk_name', 'Unnamed Risk')} — {risk.get('severity', 'Unknown')}"):
                st.markdown(f"**Description:** {risk.get('description', 'Not specified')}")
                st.markdown(f"**Why it matters:** {risk.get('reason', 'Not specified')}")
                st.markdown(f"**Suggested action:** {risk.get('suggested_action', 'Not specified')}")
                if risk.get("page_number"):
                    st.caption(f"Reference: Page {risk.get('page_number')}")

    # --- Fine Print ---
    with tab_fineprint:
        alerts = data.get("fine_print_alerts") or []
        st.markdown("### 🚩 Fine Print Alerts")
        if not alerts:
            st.info("No notable fine print was flagged.")
        for alert in alerts:
            with st.container(border=True):
                st.markdown(f"**🚩 {alert.get('title', 'Alert')}**")
                st.caption(alert.get("explanation", ""))

    # --- Fairness ---
    with tab_fairness:
        fairness = data.get("fairness") or {}
        st.markdown("### ⚖️ Fairness Analysis")
        with st.container(border=True):
            client_pct = fairness.get("client_friendly_percent", 0)
            vendor_pct = fairness.get("vendor_friendly_percent", 0)
            st.markdown(f"**Client Friendly:** {client_pct}%")
            st.progress(min(max(int(client_pct or 0), 0), 100) / 100)
            st.markdown(f"**Vendor Friendly:** {vendor_pct}%")
            st.progress(min(max(int(vendor_pct or 0), 0), 100) / 100)
            st.markdown(f"**Balanced:** {fairness.get('balanced', 'Not specified')}")
            st.caption(fairness.get("explanation", ""))

    # --- Checklist ---
    with tab_checklist:
        checklist = data.get("before_you_sign_checklist") or []
        st.markdown("### 📋 Before You Sign Checklist")
        if not checklist:
            st.info("No checklist items were generated.")
        for item in checklist:
            st.checkbox(item, key=f"chk_{hash(item)}")

    # --- Missing Clauses ---
    with tab_missing:
        missing = data.get("missing_clauses") or []
        st.markdown("### 🔍 Missing Clauses")
        if not missing:
            st.success("No commonly expected clauses appear to be missing.")
        for m in missing:
            with st.container(border=True):
                st.markdown(f"**❌ {m.get('clause', 'Unnamed Clause')}**")
                st.caption(m.get("importance", ""))


# ----------------------------
# Chat handling
# ----------------------------

def process_prompt(prompt: str, client: Groq, model_name: str, system_prompt: str):
    """Send a prompt (typed or from a suggestion button) through the chat flow."""

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    groq_messages = [{"role": "system", "content": system_prompt}]
    groq_messages.extend(st.session_state.messages)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing document..."):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=groq_messages,
                    temperature=0.2,
                    max_tokens=1500,
                )
                answer = response.choices[0].message.content
            except Exception as exc:
                answer = f"Unable to generate response: {exc}"

        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})


# ----------------------------
# Session State
# ----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_file" not in st.session_state:
    st.session_state.active_file = ""

if "dashboard_data" not in st.session_state:
    st.session_state.dashboard_data = None


# ----------------------------
# Sidebar — controls
# ----------------------------

with st.sidebar:
    st.markdown("### ⚙️ Settings")

    uploaded_pdf = st.file_uploader(
        "Upload Legal Document",
        type=["pdf"],
        help="Upload a text-based legal agreement or contract.",
    )

    model_name = st.selectbox(
    "Groq Model",
    ["openai/gpt-oss-120b", "openai/gpt-oss-20b"],
    index=0,
)

    persona = st.selectbox("Explain as", PERSONAS, index=0)

    eli15 = st.toggle("Explain Like I'm 15", value=False)

    if st.button("Clear Chat", use_container_width=True):
        clear_chat()
        st.rerun()


# Reset chat + dashboard when file changes

current_file = uploaded_pdf.name if uploaded_pdf else ""

if current_file != st.session_state.active_file:
    clear_chat()
    st.session_state.dashboard_data = None
    st.session_state.active_file = current_file


st.title("⚖️ LegalLens AI")

if uploaded_pdf is None:
    render_landing_page()
    st.info("👈 Upload a legal document from the sidebar to begin.")
    st.stop()


try:
    with st.spinner("Reading legal document..."):
        document_text = extract_pdf_text(uploaded_pdf.getvalue())
except Exception as exc:
    st.error(f"Unable to read PDF: {exc}")
    st.stop()


if not document_text.strip():
    st.warning(
        "No readable text was found in the uploaded PDF. Please upload a text-based PDF."
    )
    st.stop()


system_prompt = build_system_prompt(document_text, persona, eli15)
client = get_groq_client()

st.success("Legal document uploaded successfully.")


# ----------------------------
# One-Click Analysis Dashboard
# ----------------------------

if st.session_state.dashboard_data is None:
    with st.spinner("Generating full analysis dashboard..."):
        st.session_state.dashboard_data = generate_dashboard_data(
            client, model_name, document_text
        )

render_dashboard(st.session_state.dashboard_data)


# ----------------------------
# Display Chat History
# ----------------------------

st.markdown("---")
st.markdown("### 💬 Ask LegalLens AI")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ----------------------------
# Chat Suggestions — always visible
# ----------------------------

st.markdown("**Suggested Questions**")
cols = st.columns(2)
for idx, question in enumerate(SUGGESTED_QUESTIONS):
    col = cols[idx % 2]
    if col.button(question, key=f"suggestion_{idx}", use_container_width=True):
        process_prompt(question, client, model_name, system_prompt)
        st.rerun()


# ----------------------------
# Chat Input
# ----------------------------

user_prompt = st.chat_input("Ask anything about the uploaded legal document...")

if user_prompt:
    process_prompt(user_prompt, client, model_name, system_prompt)
