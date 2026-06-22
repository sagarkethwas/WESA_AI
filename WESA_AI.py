import os
import sys
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin
from io import BytesIO
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import builtwith
from dotenv import load_dotenv # Import load_dotenv

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Load environment variables from .env file (for local development)
load_dotenv()

# Streamlit session state initialization
if "selected_solutions" not in st.session_state:
    st.session_state.selected_solutions = []
if "generate_clicked" not in st.session_state:
    st.session_state.generate_clicked = False

# ==================================================
# ✅ GEMINI AI SETUP
# ==================================================

import google.generativeai as genai

# Access the API key securely. Prioritize Streamlit secrets for deployment,
# fall back to environment variable (from .env or system) for local development.

gemini_api_key = None
try:
    # Try to get from Streamlit secrets (for deployed apps)
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except Exception as e: # Catch a broader Exception to handle StreamlitSecretNotFoundError
    # Fallback to os.getenv for local development with .env
    gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    st.error("GEMINI_API_KEY not found. Please set it in Streamlit secrets or in your .env file.")
else:
    genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel("models/gemini-2.5-flash")
def generate_plan(solution, industry, company_name):

    prompt = f"""
    You are an expert AI consultant.

    Company Name: {company_name}
    Industry: {industry}

    Recommended Solution:
    {solution}

    Create a detailed implementation plan.

    Include:

    1. Business Problem
    2. Proposed Solution
    3. Features
    4. Development Steps
    5. Timeline
    6. Expected Benefits
    7. Estimated ROI

    Format nicely in markdown.
    """
    try:


       response = model.generate_content(prompt)
       st.write("Gemini Raw Response:") # Added for debugging
       st.write(response.text) # Added for debugging

       # Changed for Colab visibility
       print("RAW PLAN RESPONSE")

       print(response.text)


       return response.text

    except Exception as e:
        st.error(f"PLAN ERROR: {e}") # Improved error handling
        st.code(str(e)) # Improved error handling
        print(f"PLAN ERROR: {e}") # Improved error handling
        return None # Improved error handling
import json

def generate_ai_business_analysis(
    company_name,
    industry,
    website_text,
    meta_desc,
    technologies,
    emails,
    phones,
    social_links
):

    prompt = f"""
You are a Senior Business Consultant, Digital Transformation Advisor, AI Strategist, and Enterprise Solutions Architect.
Your goal is to understand the BUSINESS behind the website, not to analyze the website itself.
You will act like a consultant preparing for an executive discovery meeting.

Analyze this company in detail, adhering to the following guidelines:
- All information in your analysis MUST be directly derived or intelligently inferred from the provided company information. Do not invent or speculate.
- Focus on business-centric outputs, avoiding website-centric recommendations or issues.
- The output must feel like a professional consulting report, not a website audit.
- Make recommendations valuable enough to discuss with CXO-level stakeholders.
- Infer business context intelligently from available data.

Company:
{company_name}

Industry (as initially detected):
{industry}

Meta Description:
{meta_desc}

Website Content (up to 12000 characters for business context):
{website_text[:12000]}

Detected Technologies:
{json.dumps(technologies) if technologies else "None detected"}

Extracted Emails:
{emails if emails else "None"}

Extracted Phones:
{phones if phones else "None"}

Extracted Social Links:
{social_links if social_links else "None"}

---

## ANALYSIS FRAMEWORK

### Step 1: Determine the company's core business aspects:
- Primary Industry: [e.g., Software, Healthcare, Manufacturing]
- Secondary Industry: [e.g., Data Analytics, Cybersecurity, Logistics] (if applicable, otherwise use 'None')
- Business Type: [e.g., B2B SaaS Company, Manufacturing Company, Healthcare Provider, Logistics Organization, Financial Services Firm, Educational Institution, E-Commerce Business, B2C Service Provider]
- Target Customers: [e.g., Small Businesses, Enterprise Clients, Consumers, Specific Demographics]
- Revenue Model: [e.g., Subscription, Transactional, Service-based, Product sales, Advertising]

### Step 2: Create a business-focused summary (Company Overview):
- What the company does
- Who it serves
- How it likely earns revenue
- What appears to be its core value proposition

### Step 3: Identify likely business challenges.
IMPORTANT: Challenges must be business challenges. DO NOT generate website issues (e.g., SEO, design, UI/UX, page speed, chatbot).
Instead, focus on:
- Lead conversion challenges
- Customer retention challenges
- Operational inefficiencies
- Manual business processes
- Data fragmentation
- Poor reporting visibility
- Sales forecasting challenges
- Service scalability challenges
- Supply chain challenges
- Workforce productivity challenges
- Compliance and governance challenges
- Customer support bottlenecks

### Step 4: Generate executive-level discovery questions (Leadership Questions).
Questions should be targeted toward CEO, COO, CTO, CIO, CMO, Sales Head, Operations Head.
Questions should help uncover:
- Growth objectives
- Revenue targets
- Customer acquisition issues
- Customer retention issues
- Operational inefficiencies
- Technology limitations
- Reporting challenges
- Data availability
- Automation opportunities
- AI adoption readiness

### Step 5: Generate practical AI opportunities specific to the organization.
Examples: AI Lead Qualification, Predictive Analytics, Demand Forecasting, Intelligent Process Automation, AI Customer Service Assistant, Knowledge Management Assistant, Fraud Detection, Smart Document Processing, Predictive Maintenance, Sales Intelligence Platform, Recommendation Systems, Process Mining.

### Step 6: Generate recommended solutions.
Every solution must be outcome-focused and include:
1. Solution Name
2. Business Problem Solved
3. Expected Business Impact
4. Estimated Value
DO NOT recommend generic items like "Build a website" or "Improve SEO".
Instead, recommend: AI Revenue Intelligence, Customer Analytics Platform, Predictive Demand Forecasting, Intelligent Automation, CRM Optimization, Customer Success Intelligence, Data Lake & Analytics Modernization, AI-Powered Support Operations, Process Mining & Workflow Automation, Enterprise Knowledge Assistant.

### Step 7: For every major recommendation, estimate impact areas (Expected Business Impact).
Impact areas: Revenue Growth, Cost Reduction, Productivity Improvement, Customer Experience, Scalability, Data Visibility, Decision Making.
Each impact area should specify an `impact_area` and an `expected_result`.

---

Return ONLY valid JSON in the following format:

```json
{{
  "company_summary": "",
  "primary_industry": "",
  "secondary_industry": "",
  "business_type": "",
  "target_customers": "",
  "revenue_model": "",
  "business_challenges": [],
  "leadership_questions": [],
  "ai_opportunities": [],
  "recommended_solutions": [],
  "expected_business_impact": []
}}
```
"""

    try:
        response = model.generate_content(prompt)

        text = response.text.strip()
        # Changed for Colab visibility
        print("RAW GEMINI RESPONSE")
        print(text)

        import re

        match = re.search(r'\{.*\}', text, re.DOTALL)

        if match:
           text = match.group()

        return json.loads(text)

    except Exception as e:


        # Keeping Streamlit error for potential app deployment, but will print in Colab
        print(f"AI Error: {str(e)}")
        st.error(f"AI Error: {str(e)}")

        return {
        "company_summary": f"AI Error: {str(e)}",
        "primary_industry": "",
        "secondary_industry": "",
        "business_type": "",
        "target_customers": "",
        "revenue_model": "",
        "business_challenges": [],
        "leadership_questions": [],
        "ai_opportunities": [],
        "recommended_solutions": [],
        "expected_business_impact": []
    }

# ==================================================
# HELPER FUNCTION FOR WEBSITE ANALYSIS
# ==================================================
def analyze_website_data(url):
    try:
        with st.spinner(f"\U0001f50d Analyzing {url}..."):
            headers = {
                "User-Agent": "Mozilla/5.0"
            }
            r = requests.get(url, headers=headers, timeout=15)
            time.sleep(1);

        soup = BeautifulSoup(r.text, "html.parser")

        for tag in soup([
            "script",
            "style",
            "noscript"
        ]):
            tag.decompose()

        raw_text = soup.get_text(separator=" ")
        raw_text = re.sub(r"\s+", " ", raw_text).strip()

        title = (soup.title.text.strip() if soup.title else "No Title Found")
        meta = soup.find("meta", attrs={"name": "description"})
        meta_desc = (meta.get("content") if meta else "No Meta Description")
        links = soup.find_all("a")
        links_count = len(links) # Get the count of all <a> tags

        logo = None
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            logo = urljoin(url, og.get("content"))
        else:
            icon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
            if icon and icon.get("href"):
                logo = urljoin(url, icon.get("href"))

        emails = list(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", raw_text)))
        phones = list(set(re.findall(r"\+?\d[\d -]{8,15}\d", raw_text)))

        social_links = []
        for a in links:
            href = a.get("href")
            if href:
                lower_href = href.lower() # Removed the extra '+'
                if any(x in lower_href for x in [
                    "linkedin", "facebook", "instagram", "twitter", "youtube"
                ]):
                    social_links.append(href)
        social_links = list(set(social_links))

        lower_text = raw_text.lower()
        industry_map = {
            "Software": ["software", "saas", "cloud", "ai", "technology"],
            "Healthcare": ["hospital", "clinic", "patient"],
            "Finance": ["bank", "finance", "insurance"],
            "Education": ["education", "school", "course"],
            "E-Commerce": ["ecommerce", "shopping", "cart"],
            "Logistics": ["delivery", "shipment", "warehouse", "transport"],
            "Real Estate": ["property", "real estate", "broker"],
            "Manufacturing": ["factory", "manufacturing", "production"]
        }

        scores = {k: sum(lower_text.count(w) for w in v) for k, v in industry_map.items()}
        industry = (max(scores, key=scores.get) if max(scores.values()) > 0 else "General Business")

        try:
            technologies = builtwith.parse(url)
        except:
            technologies = {}

        ai_score = min(100, len(emails)*10 + len(social_links)*10 + links_count) # Use links_count here
        lead_score = min(100, len(phones)*20 + len(social_links)*10 + len(emails)*15)

        ai_analysis = generate_ai_business_analysis(
            company_name=title,
            industry=industry,
            website_text=raw_text,
            meta_desc=meta_desc,
            technologies=technologies,
            emails=emails,
            phones=phones,
            social_links=social_links
        )

        return {
            "url": url,
            "title": title,
            "meta_desc": meta_desc,
            "emails": emails,
            "phones": phones,
            "social_links": social_links,
            "industry": ai_analysis["primary_industry"], # Use primary_industry from AI
            "ai_score": ai_score,
            "lead_score": lead_score,
            "raw_text": raw_text,
            "logo": logo,
            "technologies": technologies,
            "company_summary": ai_analysis["company_summary"], # New key
            "primary_industry": ai_analysis["primary_industry"], # New key
            "secondary_industry": ai_analysis["secondary_industry"], # New key
            "business_type": ai_analysis["business_type"], # New key
            "target_customers": ai_analysis["target_customers"], # New key
            "revenue_model": ai_analysis["revenue_model"], # New key
            "business_challenges": ai_analysis["business_challenges"], # New key
            "leadership_questions": ai_analysis["leadership_questions"], # New key
            "ai_opportunities": ai_analysis["ai_opportunities"], # New key
            "recommended_solutions": ai_analysis["recommended_solutions"], # New key
            "expected_business_impact": ai_analysis["expected_business_impact"], # New key
            "links_count": links_count
        }

    except Exception as e:
        import traceback
        st.error(f"ERROR analyzing {url}: {str(e)}")
        print(f"ERROR analyzing {url}: {str(e)}")
        print(traceback.format_exc())
        return None

# ======================================================k
# PAGE CONFIG
# ======================================================k

st.set_page_config(
    page_title="NextGen WESA AI",
    page_icon="\U0001f680",
    layout="wide"
)

# ======================================================k
# PREMIUM UI
# ==================================================k

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg,#020617,#0f172a,#111827);
    color: white;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.title {
    font-size: 4.2rem;
    font-weight: 900;
    text-align: center;
    margin-top: 15px;

    background: linear-gradient(
        90deg,
        #38bdf8,
        #8b5cf6,
        #06b6d4
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #cbd5e1;
    margin-bottom: 30px;
}

.glass {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 24px;
    margin-top: 16px;
}

.stTextInput input {
    background: rgba(255,255,255,0.08);
    color: white;
    border-radius: 14px;
}

.stButton>button {
    background: linear-gradient(
        90deg,
        #06b6d4,
        #3b82f6,
        #8b5cf6
    );

    border: none;
    border-radius: 14px;
    height: 50px;
    font-weight: bold;
}

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border-radius: 16px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #020617,
        #0f172a
    );
}

</style>
""", unsafe_allow_html=True)

# ======================================================k
# HEADER
# ======================================================k

st.markdown("""
<div class='title'>
\U0001f680 NEXTGEN WESA AI
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='subtitle'>
AI Powered Website Intelligence Platform
</div>
""", unsafe_allow_html=True)

# ==================================================k
# HERO CARDS
# ==================================================k

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.info("\U0001f9f2 AI  Detection")

with c2:
    st.success("\U0001f4c8 Smart  Analytics")

with c3:
    st.warning("\U000026a1 Insights")

with c4:
    st.error("\U0001f525 Lead Intel")

st.divider()

# ==================================================k
# SIDEBAR
# ==================================================k

st.sidebar.title("\U00002699\U0000fe0f AI Platform Features")

st.sidebar.success("""
\u2705 Website Scraping
\u2705 Company Summary
\u2705 Industry Detection
\u2705 Contact Extraction
\u2705 Business Analysis
\u2705 Discovery Questions
\u2705 AI Solution Suggestions
\u2705 Technology Detection
\u2705 PDF Export
"""
)

# ==================================================k
# INPUT
# ==================================================k

url = st.text_input(
    "\U0001f310 Enter Company Website URL",
    value="https://cloud.google.com/blog/topics/developers-practitioners/run-streamlit-apps-google-cloud-run", # Added a more relevant default URL
    placeholder="https://example.com"
)

competitor_urls_input = st.text_area(
    "Enter Competitor Website URLs (one per line)",
    placeholder="https://competitor1.com\nhttps://competitor2.com"
)

analyze = st.button("\U0001f680 Analyze Website")

# ==================================================k
# MAIN LOGIC
# ==================================================k

if analyze or st.session_state.get("data_ready"):

    if not url:
        st.warning("Please enter website URL")
        st.stop()

    # Analyze main URL
    main_company_data = analyze_website_data(url)
    if main_company_data is None:
        st.stop()

    st.session_state["data_ready"] = True
    st.session_state.data = main_company_data

    # Analyze competitor URLs
    competitor_data = []

    if competitor_urls_input:
        urls = [u.strip() for u in competitor_urls_input.split('\n') if u.strip()]
        for comp_url in urls:
            comp_analysis = analyze_website_data(comp_url)
            if comp_analysis:
                competitor_data.append(comp_analysis)
    st.session_state.competitor_data = competitor_data

    # Extract main company data for ease of access
    title = st.session_state.data["title"]
    meta_desc = st.session_state.data["meta_desc"]
    emails = st.session_state.data["emails"]
    phones = st.session_state.data["phones"]
    social_links = st.session_state.data["social_links"]
    # Updated from 'industry' to use new AI analysis fields
    primary_industry = st.session_state.data["primary_industry"]
    secondary_industry = st.session_state.data["secondary_industry"]
    business_type = st.session_state.data["business_type"]
    target_customers = st.session_state.data["target_customers"]
    revenue_model = st.session_state.data["revenue_model"]

    ai_score = st.session_state.data["ai_score"]
    lead_score = st.session_state.data["lead_score"]
    raw_text = st.session_state.data["raw_text"]
    logo = st.session_state.data["logo"]
    technologies = st.session_state.data["technologies"]

    company_summary = st.session_state.data["company_summary"]
    business_challenges = st.session_state.data["business_challenges"]
    leadership_questions = st.session_state.data["leadership_questions"]
    ai_opportunities = st.session_state.data["ai_opportunities"]
    recommended_solutions = st.session_state.data["recommended_solutions"]
    expected_business_impact = st.session_state.data["expected_business_impact"]
    links_count = st.session_state.data["links_count"]

    # ==================================================k
    # SIDEBAR DETECTED FEATURES
    # ==================================================k

    st.sidebar.markdown(
        "### \U0001f50d Website Features Detected"
    )

    st.sidebar.write(
        "\U0001f3e2 Primary Industry:",
        primary_industry
    )
    if secondary_industry and secondary_industry != 'None':
        st.sidebar.write(
            "\U0001f3ed Secondary Industry:",
            secondary_industry
        )

    st.sidebar.write(
        "\U0001f3ad Logo:",
        "Yes" if logo else "No"
    )

    st.sidebar.write(
        "\U00002709\U0000fe0f Emails:",
        len(emails)
    )

    st.sidebar.write(
        "\U0001f4f1 Phones:",
        len(phones)
    )

    st.sidebar.write(
        "\U0001f310 Social Links:",
        len(social_links)
    )

    st.sidebar.write(
        "\U00002699\U0000fe0f Technologies:",
        "Yes" if technologies else "No"
    )

    # ==================================================k
    # TABS
    # ==================================================k

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "\U0001f4ca Dashboard",
        "\U0001f4de Contacts",
        "\U0001f4c8 Insights",
        "\U0001f4c4 Website Review",
        "\U0001f9e0 AI Recommendations",
        "\U00002694\U0000fe0f Competitor Analysis"
    ])

    # ==================================================k
    # TAB 1 — DASHBOARD
    # ==================================================k

    with tab1:
        if logo:
            st.image(logo, width=120)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Emails", len(emails))
        c2.metric("Phones", len(phones))
        c3.metric("Links", links_count) # Use the new links_count variable
        c4.metric("Social", len(social_links))

        st.markdown(f"""
        <div class="glass">
        <h2>\U0001f3e2 Company Overview</h2>
        <p><b>Company Name:</b> {title}</p>
        <p><b>Primary Industry:</b> {primary_industry}</p>
        <p><b>Secondary Industry:</b> {secondary_industry if secondary_industry != 'None' else 'N/A'}</p>
        <p><b>Business Type:</b> {business_type}</p>
        <p><b>Target Customers:</b> {target_customers}</p>
        <p><b>Revenue Model:</b> {revenue_model}</p>
        <p><b>AI Score:</b> {ai_score}%</p>
        <p><b>Lead Score:</b> {lead_score}%</p>
        <p><b>Meta Description:</b> {meta_desc}</p>
        <p><b>AI Summary:</b> {company_summary}</p>
        </div>
        """, unsafe_allow_html=True)

        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ai_score,
            title={'text': 'AI Readiness'},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': '#06b6d4'}
            }
        ))
        gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': 'white'})
        st.plotly_chart(gauge, use_container_width=True)

    # ==================================================k
    # TAB 2 — CONTACTS
    # ==================================================k

    with tab2:
        st.subheader("\U00002709\U0000fe0f Emails")
        st.write(emails or "No emails found")

        st.subheader("\U0001f4f1 Phone Numbers")
        st.write(phones or "No phone numbers found")

        st.subheader("\U0001f310 Social Links")
        st.write(social_links or "No social links found")

    # ==================================================k
    # TAB 3 — INSIGHTS
    # ==================================================k

    with tab3:
        st.markdown("""
        <div class="glass">
        <h3>\U0001f4c8 Business Insights</h3>
        </div>
        """, unsafe_allow_html=True)

        st.success(
            "\u2705 Digital Presence: Strong"
            if len(raw_text.split()) > 1000
            else "\u2705 Digital Presence: Moderate"
        )

        st.success(
            "\u2705 Contact Accessibility: Good"
            if emails or phones
            else "\u2705 Contact Accessibility: Limited"
        )

        st.success(
            "\u2705 Social Presence Detected"
            if social_links
            else "\u2705 Limited Social Presence"
        )

        st.success(
            "\u2705 AI & Automation Readiness: High"
            if ai_score > 60
            else "\u2705 AI & Automation Readiness: Medium"
        )

        insight_df = pd.DataFrame({
            "Metric": ["Content", "Contacts", "Social", "Automation"],
            "Score": [
                min(100, len(raw_text.split()) // 10),
                80 if emails or phones else 40,
                70 if social_links else 25,
                ai_score
            ]
        })

        fig = px.bar(
            insight_df,
            x="Metric",
            y="Score",
            template="plotly_dark",
            color="Metric"
        )

        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

        if technologies:
            st.subheader("\U00002699\U0000fe0f Detected Technologies")
            st.json(technologies)

    # ==================================================k
    # TAB 4 — WEBSITE REVIEW
    # ==================================================k

    with tab4:
        st.markdown("""
        <div class='glass'>
        <h3>\U0001f4c4 Website Content Review</h3>
        </div>
        """, unsafe_allow_html=True)

        sentences = re.split(r'(?<=[.!?])\s+', raw_text)
        paragraphs = []
        temp = ""

        for s in sentences:
            temp += s + " "
            if len(temp.split()) >= 130:
                paragraphs.append(temp.strip())
                temp = ""
        if temp:
            paragraphs.append(temp.strip())

        for i, p in enumerate(paragraphs[:6]):
            st.markdown(f"""
            <div class=\"glass\">
            <h4>\U0001f4cd Section {i+1}</h4>
            <p style="
            line-height:1.8;
            text-align:justify;
            ">
            {p}
            </p>
            </div>
            """, unsafe_allow_html=True)

    # ==================================================k
    # TAB 5 — AI RECOMMENDATIONS
    # ==================================================k

    with tab5:
        st.markdown(f"""
         <div class=\"glass\">
       <h2>\U0001f9e0 AI Company Summary</h2>
       <p>{company_summary}</p>
       </div>
       """, unsafe_allow_html=True)

        st.markdown("""
       <div class=\"glass\">
       <h2>\u26a0\u00ef\u00b8\u008f Business Challenges</h2>
       </div>
       """, unsafe_allow_html=True)

        if business_challenges:
            for challenge in business_challenges:
                st.warning(challenge)
        else:
            st.info("No specific business challenges identified.")

        st.markdown("""
       <div class=\"glass\">
       <h2>\u2753 Leadership Discovery Questions</h2>
       </div>
       """, unsafe_allow_html=True)

        if leadership_questions:
            for q in leadership_questions:
                st.write(f"\u2705 {q}")
        else:
            st.info("No leadership discovery questions generated.")

        st.markdown("""
       <div class=\"glass\">
       <h2>\U0001f4a1 AI Opportunities</h2>
       </div>
       """, unsafe_allow_html=True)

        if ai_opportunities:
            for opp in ai_opportunities:
                st.success(opp)
        else:
            st.info("No specific AI opportunities identified.")

        st.markdown("""
       <div class=\"glass\">
       <h2>\U0001f680 Recommended Solutions</h2>
       </div>
       """, unsafe_allow_html=True)

        if recommended_solutions:
            has_valid_solutions = False
            for solution in recommended_solutions:
                solution_name = solution.get('solution_name')
                # Only display the solution block if solution_name is not None, not empty, not just whitespace, and not 'N/A'
                if solution_name and solution_name.strip() and solution_name.strip().lower() != 'n/a':
                    has_valid_solutions = True
                    st.markdown(f"""
                    <div class=\"glass\">
                    <h4>{solution_name.strip()}</h4>
                    </div>
                    """, unsafe_allow_html=True)
            if not has_valid_solutions:
                st.info("No specific or valid solutions recommended by the AI.")
        else:
            st.info("No specific solutions recommended.")

        st.markdown("""
       <div class=\"glass\">
       <h2>\U0001f4c8 Expected Business Impact</h2>
       </div>
       """, unsafe_allow_html=True)
        if expected_business_impact:
            for impact in expected_business_impact:
                st.info(f"**{impact.get('impact_area', 'N/A')}:** {impact.get('expected_result', 'N/A')}")
        else:
            st.info("No specific business impact details provided.")

        st.markdown("""
       <div class=\"glass\">
       <h2>\U0001f916 AI Solutions Chatbot</h2>
       </div>
       """, unsafe_allow_html=True)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_question = st.text_input(
            "Ask about the suggested solutions:",
            key="solution_chatbot_input"
        )

        ask_solution_button = st.button("Ask AI")

        if ask_solution_button and user_question:
            st.session_state.chat_history.append({"role": "user", "content": user_question})

            with st.spinner("AI is thinking..."):
                chat_prompt = f"""
                You are an expert AI consultant discussing business solutions.
                Here are some suggested solutions for the company:
                {json.dumps(recommended_solutions, indent=2)}

                The user's question is: "{user_question}"

                Please answer the user's question based on the provided solutions and your expertise.
                If the user asks for a detailed plan for a specific solution, instruct them to ask for it separately, or just provide a summary.
                Keep the response concise and helpful.
                """
                try:
                    chat_response = model.generate_content(chat_prompt)
                    ai_answer = chat_response.text
                    st.session_state.chat_history.append({"role": "ai", "content": ai_answer})
                except Exception as e:
                    st.error(f"Chatbot Error: {e}")
                    st.session_state.chat_history.append({"role": "ai", "content": f"Sorry, I encountered an error: {e}"})

        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f"**You:** {chat['content']}")
            else:
                st.markdown(f"**AI:** {chat['content']}")

    # ==================================================k
    # TAB 6 — COMPETITOR ANALYSIS
    # ==================================================k
    with tab6:
        st.markdown("""
        <div class='glass'>
        <h3>\U00002694\U0000fe0f Competitor Analysis</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get('competitor_data'):
            all_companies_data = [st.session_state.data] + st.session_state.competitor_data
            comparison_df = pd.DataFrame([
                {
                    'Company': d['title'],
                    'URL': d['url'],
                    'Primary Industry': d['primary_industry'],
                    'Business Type': d['business_type'],
                    'AI Score': d['ai_score'],
                    'Lead Score': d['lead_score'],
                    'Emails Found': len(d['emails']),
                    'Phones Found': len(d['phones']),
                    'Social Links Found': len(d['social_links']),
                    'Technologies': ', '.join(tech for cat in d['technologies'].values() for tech in cat) if d['technologies'] else 'None'
                }
                for d in all_companies_data
            ])

            st.subheader("Overall Comparison Table")
            st.dataframe(comparison_df.set_index('Company'))

            st.subheader("AI Score Comparison")
            fig_ai = px.bar(comparison_df, x='Company', y='AI Score', color='Company', title='AI Score Comparison', template='plotly_dark')
            fig_ai.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': 'white'})
            st.plotly_chart(fig_ai, use_container_width=True)

            st.subheader("Lead Score Comparison")
            fig_lead = px.bar(comparison_df, x='Company', y='Lead Score', color='Company', title='Lead Score Comparison', template='plotly_dark')
            fig_lead.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': 'white'})
            st.plotly_chart(fig_lead, use_container_width=True)

            st.subheader("Contact Information Comparison")
            contact_df = comparison_df[['Company', 'Emails Found', 'Phones Found', 'Social Links Found']]
            contact_melted_df = contact_df.melt(id_vars=['Company'], var_name='Contact Type', value_name='Count')
            fig_contact = px.bar(contact_melted_df, x='Company', y='Count', color='Contact Type', title='Contact Information Comparison', barmode='group', template='plotly_dark')
            fig_contact.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': 'white'})
            st.plotly_chart(fig_contact, use_container_width=True)

            st.subheader("AI-Generated Comparative Insights")
            # Prepare data for comparative AI analysis
            all_companies_summary_data = []
            for d in all_companies_data:
                all_companies_summary_data.append({
                    'company': d['title'],
                    'url': d['url'],
                    'primary_industry': d['primary_industry'],
                    'secondary_industry': d['secondary_industry'],
                    'business_type': d['business_type'],
                    'target_customers': d['target_customers'],
                    'revenue_model': d['revenue_model'],
                    'ai_score': d['ai_score'],
                    'lead_score': d['lead_score'],
                    'company_summary': d['company_summary'],
                    'business_challenges': d['business_challenges'],
                    'leadership_questions': d['leadership_questions'],
                    'ai_opportunities': d['ai_opportunities'],
                    'recommended_solutions': d['recommended_solutions'],
                    'expected_business_impact': d['expected_business_impact'],
                    'emails_count': len(d['emails']),
                    'phones_count': len(d['phones']),
                    'social_links_count': len(d['social_links']),
                    'technologies_summary': ', '.join(tech for cat in d['technologies'].values() for tech in cat) if d['technologies'] else 'None'
                })

            comparative_prompt = f"""
            You are an expert Business Consultant providing a comparative analysis of multiple companies.
            Review the following data for each company and provide a concise, insightful comparison.
            Focus on key differences and similarities in their business summaries, challenges, recommended solutions,
            AI readiness (AI Score), lead generation potential (Lead Score), and digital presence (contacts, social links, technologies).

            When comparing well-known, market-leading companies (e.g., Google, Microsoft), leverage your extensive general knowledge about their scale,
            market influence, typical strengths, and common challenges, in addition to the provided scraped data.
            This will help in generating more meaningful and strategic comparative insights.

            Companies Data:
            {json.dumps(all_companies_summary_data, indent=2)}

            Please provide:
            1.  A high-level comparative summary highlighting overall strengths and weaknesses across companies.
            2.  Key differentiating factors for each company based on their scores, technologies, and AI analysis.
            3.  Common challenges or opportunities identified across the group.
            4.  Strategic implications or advice for the main company (the first one in the list).

            Format your response in markdown.
            """

            with st.spinner("\U0001f9e0 Generating comparative AI insights..."):
                try:
                    comparative_response = model.generate_content(comparative_prompt)
                    st.markdown(comparative_response.text)
                except Exception as e:
                    st.error(f"Error generating comparative insights: {e}")
                    print(f"Error generating comparative insights: {e}")

        else:
            st.info("Enter competitor URLs above to perform a comparison.")


    # ==================================================k
    # PDF EXPORT
    # ==================================================k

    pdf_buffer = BytesIO()

    pdf = canvas.Canvas(
        pdf_buffer,
        pagesize=letter
    )

    pdf.drawString(
        50,
        750,
        "NEXTGEN AI DISCOVERY REPORT"
    )

    pdf.drawString(
        50,
        720,
        f"Website: {url}"
    )

    pdf.drawString(
        50,
        700,
        f"Primary Industry: {primary_industry}"
    )

    pdf.drawString(
        50,
        680,
        f"Business Type: {business_type}"
    )

    pdf.drawString(
        50,
        660,
        f"AI Score: {ai_score}%"
    )

    pdf.drawString(
        50,
        640,
        f"Lead Score: {lead_score}%"
    )

    # Add business challenges to PDF
    y_position = 620
    pdf.drawString(50, y_position, "Business Challenges:")
    y_position -= 20
    if business_challenges:
        for i, challenge in enumerate(business_challenges[:5]): # Limit to 5 for brevity
            pdf.drawString(70, y_position, f"- {challenge}")
            y_position -= 15
    else:
        pdf.drawString(70, y_position, "No specific business challenges identified.")
    y_position -= 20

    # Add recommended solutions to PDF
    pdf.drawString(50, y_position, "Recommended Solutions:")
    y_position -= 20
    valid_pdf_solutions = []
    for s in recommended_solutions:
        solution_name = s.get('solution_name')
        if solution_name and solution_name.strip() and solution_name.strip().lower() != 'n/a':
            valid_pdf_solutions.append(s)

    if valid_pdf_solutions:
        for i, solution in enumerate(valid_pdf_solutions[:3]): # Limit to 3 for brevity
            pdf.drawString(70, y_position, f"- {solution.get('solution_name', 'N/A')} (Impact: {solution.get('expected_impact', 'N/A')})")
            y_position -= 15
    else:
        pdf.drawString(70, y_position, "No specific solutions recommended.")

    pdf.save()

    pdf_buffer.seek(0);

    st.download_button(

        "\U0001f5c3\u00ef\u00b8\u008f Download PDF Report",

        data=pdf_buffer,

        file_name="AI_Discovery_Report.pdf",

        mime="application/pdf"
    )

else:
    # Initial state when app loads or after a full reset
    st.info("Enter a website URL and click 'Analyze Website' to get started.")

# ==================================================k
# FOOTER
# ==================================================k

st.caption("Generated for smart analysis")
