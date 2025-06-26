import streamlit as st
import PyPDF2
import docx
import json
import requests
import openai
from serpapi import GoogleSearch

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Career Co-Pilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

css_template = """
<style>
    div[data-testid="stAppViewContainer"] > .main {{
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    div[data-testid="stAppViewContainer"] > .main .block-container {{
        background: transparent !important;
        padding-top: 2rem; 
    }}

    div[data-testid="stSidebar"] {{
        background-color: #f0f2f6 !important;
    }}

    div[data-testid="stSidebar"] * {{
        color: #000000 !important;
    }}
    
    div[data-testid="stSidebar"] .st-emotion-cache-16txtl3 {{
        background-color: rgba(230, 243, 255, 1) !important;
        border: 1px solid #91d5ff;
        border-radius: 8px;
    }}
    div[data-testid="stSidebar"] .stAlert {{
        background-color: #f6ffed !important;
        border: 1px solid #b7eb8f;
    }}

    div[data-testid="stFileUploader"] {{
        background-color: #ffffff;
        border: 1px dashed #cccccc;
        border-radius: 10px;
    }}
    div[data-testid="stFileUploader"] button {{
        border-color: #cccccc !important;
        background-color: #ffffff !important;
        color: #ff4b4b !important;
    }}

    .main h1, .main h2, .main h3, .main h4, .main p, .main .stMarkdown, .main div[data-testid="stText"] {{
        color: #ffffff !important;
    }}
    
    .main .st-emotion-cache-16txtl3,
    .main div[data-testid="stExpander"],
    .main .st-emotion-cache-q8sbsg,
    .main .stTabs [data-baseweb="tab-list"] {{
        background-color: rgba(13, 17, 23, 0.7) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
    }}
    .main .stButton>button {{
        background-color: #238636 !important;
    }}

</style>
"""
# --- Helper Functions ---
@st.cache_data
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

@st.cache_data
def read_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

@st.cache_data
def load_skills(filepath="skills_db.json"):
    with open(filepath, 'r') as f:
        return json.load(f)

# --- API Functions ---
def get_ai_analysis(resume_text, job_description):
    prompt = f"Analyze this resume against the job description...\n**RESUME:**\n{resume_text}\n\n**JOB DESCRIPTION:**\n{job_description}\n\nProvide: 1. **📊 Match Score:**... 2. **🎯 Missing Keywords:**... 3. **✍️ Summary Improvement:**... 4. **🚀 Actionable Advice:**..."
    try:
        response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "You are a career coach."}, {"role": "user", "content": prompt}], temperature=0.5)
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI analysis error: {e}"); return None

### NEW AI-POWERED FUNCTION TO GET JOB TITLES ###
def get_job_search_terms(resume_text):
    prompt = f"""
    You are an expert recruitment AI. Analyze the following resume text.
    Based on the content, identify the top 3 most likely job titles this person would be qualified for.
    Return ONLY a Python-parsable list of strings. Do not include any explanation or other text.

    Example output: ["Data Analyst", "Business Intelligence Developer", "SQL Developer"]

    Resume:
    {resume_text}
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You return only Python-parsable lists of strings."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        # The response will be a string '["Title 1", "Title 2"]', so we parse it
        search_terms = json.loads(response.choices[0].message.content)
        return search_terms
    except Exception as e:
        st.error(f"Could not generate AI search terms: {e}")
        # Fallback to generic terms if the AI fails
        return ["Data Analyst", "Software Engineer", "Project Manager"]

def find_jobs(search_term):
    query = f"{search_term} jobs in USA"
    params = {"engine": "google_jobs", "q": query, "api_key": st.secrets["SERPAPI_API_KEY"]}
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        return results.get("jobs_results", [])
    except Exception as e:
        st.error(f"Could not connect to the job search API for term '{search_term}': {e}")
        return []

# --- Initialize Session State ---
if "resume_text" not in st.session_state: st.session_state.resume_text = ""
if "resume_skills" not in st.session_state: st.session_state.resume_skills = []
if "chat_messages" not in st.session_state: st.session_state.chat_messages = []

# --- UI Layout ---
st.title("🤖 AI Career Co-Pilot")

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>Your Resume</h2>", unsafe_allow_html=True)
    resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=['pdf', 'docx'], label_visibility="collapsed")
    
    if resume_file:
        with st.spinner("Parsing resume..."):
            if resume_file.type == "application/pdf":
                st.session_state.resume_text = read_pdf(resume_file)
            else:
                st.session_state.resume_text = read_docx(resume_file)
            
            all_skills = load_skills()
            st.session_state.resume_skills = [skill for skill in all_skills if skill.lower() in st.session_state.resume_text.lower()]
        
        st.success("✅ Resume uploaded successfully!")
        st.info(f"**Detected Skills:** {', '.join(st.session_state.resume_skills) if st.session_state.resume_skills else 'None found'}")

# --- Main Content Tabs ---
tab1, tab2, tab3 = st.tabs([
    "**🔍 Resume Analyzer**", 
    "**👔 Job Recommender**", 
    "**💬 Career Chatbot**"
])

# --- TAB 1: Resume Analyzer ---
with tab1:
    st.markdown("<h3 style='text-align: center;'>Analyze Resume Against a Job Description</h3>", unsafe_allow_html=True)
    
    if st.session_state.resume_text:
        jd_col, analysis_col = st.columns([1, 1], gap="large")
        
        with jd_col:
            st.markdown("#### Paste Job Description Here:")
            job_description = st.text_area("Job Description", height=400, label_visibility="collapsed")
            analyze_button = st.button("Analyze Now", type="primary", use_container_width=True)

        with analysis_col:
            st.markdown("#### AI Analysis Report:")
            if analyze_button and job_description:
                with st.spinner("🤖 AI is analyzing... This might take a moment."):
                    ai_feedback = get_ai_analysis(st.session_state.resume_text, job_description)
                    if ai_feedback:
                        st.markdown(ai_feedback)
            elif analyze_button and not job_description:
                st.warning("Please paste a job description to analyze.")
            else:
                st.info("Your analysis report will appear here.")
    else:
        st.warning("Please upload your resume in the sidebar to activate the analyzer.")

# --- TAB 2: Job Recommender with NEW AI LOGIC ---
with tab2:
    st.markdown("<h3 style='text-align: center;'>Discover Job Opportunities</h3>", unsafe_allow_html=True)
    
    if st.session_state.resume_text:
        search_button = st.button("Find Jobs For Me", use_container_width=True)
        if search_button:
            with st.spinner("🤖 AI is generating job titles for your resume..."):
                search_terms = get_job_search_terms(st.session_state.resume_text)
                st.info(f"AI suggests searching for: **{', '.join(search_terms)}**")

            with st.spinner(" searching for the best roles for you..."):
                all_jobs = []
                for term in search_terms:
                    jobs_for_term = find_jobs(term)
                    all_jobs.extend(jobs_for_term)
                
                # Remove duplicate jobs to show a clean list
                unique_jobs = []
                seen_titles_and_companies = set()
                for job in all_jobs:
                    identifier = (job.get('title'), job.get('company_name'))
                    if identifier not in seen_titles_and_companies:
                        unique_jobs.append(job)
                        seen_titles_and_companies.add(identifier)

                if unique_jobs:
                    st.success(f"Found {len(unique_jobs)} relevant jobs!")
                    for job in unique_jobs:
                        with st.container(border=True):
                            st.subheader(job.get('title'))
                            st.write(f"**🏢 Company:** {job.get('company_name')} | **📍 Location:** {job.get('location')}")
                            with st.expander("Show Job Description"):
                                st.markdown(job.get('description', 'N/A'))
                            if apply_link := job.get('related_links', [{}])[0].get('link'):
                                st.link_button("Apply Here ➔", apply_link, use_container_width=True)
                else:
                    st.error("Could not find any jobs with the AI-suggested titles. This could be due to SerpApi account limits or a temporary issue.")
    else:
        st.warning("Upload a resume in the sidebar to find relevant jobs.")

# --- TAB 3: Career Chatbot ---
with tab3:
    st.markdown("<h3 style='text-align: center;'>Chat with Your AI Career Coach</h3>", unsafe_allow_html=True)
    
    if st.session_state.resume_text:
        chat_container = st.container(height=400)
        
        for message in st.session_state.chat_messages:
            with chat_container:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("What would you like to ask?"):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        full_prompt = f"Context: User's resume is:\n{st.session_state.resume_text}\n\nQuestion: {prompt}"
                        response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "You are a friendly and encouraging career coach chatbot."}, {"role": "user", "content": full_prompt}])
                        assistant_response = response.choices[0].message.content
                        st.markdown(assistant_response)
            
            st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})
    else:
        st.warning("Upload a resume in the sidebar to activate the chatbot.")