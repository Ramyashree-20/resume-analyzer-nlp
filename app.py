import streamlit as st
import PyPDF2
import docx
import json
import requests
import hashlib
import os
from groq import Groq
from serpapi import GoogleSearch
from streamlit_lottie import st_lottie

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Career Co-Pilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Groq Client ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Session State Init ---
for key, default in {
    "authenticated": False,
    "current_user": "",
    "resume_text": "",
    "resume_skills": [],
    "chat_messages": [],
    "auth_mode": "login"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ==========================================
# AUTH FUNCTIONS
# ==========================================
USERS_FILE = "users.json"

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def authenticate(username, password):
    users = load_users()
    return username in users and users[username]["password"] == hash_pw(password)

def register_user(username, email, password):
    users = load_users()
    if username in users:
        return False, "Username already exists"
    if any(u["email"] == email for u in users.values()):
        return False, "Email already registered"
    users[username] = {"email": email, "password": hash_pw(password)}
    save_users(users)
    return True, "Account created successfully!"

# ==========================================
# HELPER FUNCTIONS
# ==========================================
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
    return "\n".join([p.text for p in doc.paragraphs])

@st.cache_data
def load_skills(filepath="skills_db.json"):
    with open(filepath, 'r') as f:
        return json.load(f)

def load_lottie_url(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# ==========================================
# API FUNCTIONS
# ==========================================
def get_ai_analysis(resume_text, job_description):
    prompt = f"""Analyze this resume against the job description. Be thorough and specific.
**RESUME:**
{resume_text}

**JOB DESCRIPTION:**
{job_description}

Provide:
1. **📊 Match Score:** (percentage + explanation)
2. **🎯 Missing Keywords:** (important keywords from JD missing in resume)
3. **✍️ Summary Improvement:** (improved professional summary)
4. **🚀 Actionable Advice:** (3-5 specific steps)"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are an expert career coach."}, {"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI analysis error: {e}")
        return None

def get_job_search_terms(resume_text):
    prompt = f"""You are an expert recruitment AI. Analyze the following resume.
Identify the top 3 most likely job titles this person would be qualified for.
Return ONLY a Python-parsable list of strings.
Example: ["Data Analyst", "BI Developer", "SQL Developer"]

Resume:
{resume_text}"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You return only Python-parsable lists of strings."}, {"role": "user", "content": prompt}],
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Could not generate AI search terms: {e}")
        return ["Data Analyst", "Software Engineer", "Project Manager"]

def find_jobs(search_term, location="USA", experience="Any"):
    exp_prefix = "" if experience == "Any" else f"{experience} "
    q = f"{exp_prefix}{search_term} jobs in {location}"
    params = {"engine": "google_jobs", "q": q, "api_key": st.secrets["SERPAPI_API_KEY"]}
    try:
        search = GoogleSearch(params)
        return search.get_dict().get("jobs_results", [])
    except Exception as e:
        st.error(f"Job search error for '{search_term}': {e}")
        return []

# ==========================================
# CSS INJECTION
# ==========================================
def inject_css():
    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
    :root {
        --accent: #6366f1; --accent2: #8b5cf6; --accent3: #ec4899;
        --bg-dark: #0a0a1a; --bg-card: rgba(15,23,42,0.7);
        --text-w: #f1f5f9; --text-m: #94a3b8; --text-d: #64748b;
        --glass-border: rgba(99,102,241,0.15);
    }
    *:not(.material-symbols-rounded):not(.material-icons):not(svg):not(svg *) { font-family: 'Inter', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #0a0a1a 0%, #0f172a 30%, #1e1b4b 70%, #0a0a1a 100%) !important; }
    [data-testid="stHeader"] { background: transparent !important; }

    /* === Animations === */
    @keyframes fadeInUp { from { opacity:0; transform:translateY(30px); } to { opacity:1; transform:translateY(0); } }
    @keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
    @keyframes slideInLeft { from { opacity:0; transform:translateX(-50px); } to { opacity:1; transform:translateX(0); } }
    @keyframes float { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-12px); } }
    @keyframes glow { 0%,100% { box-shadow:0 0 5px rgba(99,102,241,0.2); } 50% { box-shadow:0 0 25px rgba(99,102,241,0.4); } }
    @keyframes gradientFlow { 0% { background-position:0% 50%; } 50% { background-position:100% 50%; } 100% { background-position:0% 50%; } }
    @keyframes scaleIn { from { opacity:0; transform:scale(0.9); } to { opacity:1; transform:scale(1); } }
    @keyframes borderPulse { 0%,100% { border-color:rgba(99,102,241,0.2); } 50% { border-color:rgba(139,92,246,0.5); } }

    /* === Floating BG Orbs === */
    .bg-orbs { position:fixed; inset:0; z-index:-1; pointer-events:none; overflow:hidden; }
    .orb { position:absolute; border-radius:50%; filter:blur(80px); opacity:0.12; animation:float 8s ease-in-out infinite; }
    .orb-1 { width:400px; height:400px; background:#6366f1; top:-100px; right:-100px; }
    .orb-2 { width:350px; height:350px; background:#ec4899; bottom:-80px; left:-80px; animation-delay:-3s; }
    .orb-3 { width:300px; height:300px; background:#06b6d4; top:50%; left:50%; animation-delay:-5s; }

    /* === Form Inputs === */
    .stTextInput > div > div > input {
        background: rgba(15,23,42,0.6) !important; border:1px solid rgba(99,102,241,0.2) !important;
        border-radius:12px !important; color:#f1f5f9 !important; padding:14px 16px !important;
        font-size:0.95rem !important; transition:all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus { border-color:#6366f1 !important; box-shadow:0 0 0 3px rgba(99,102,241,0.15) !important; }
    .stTextInput > div > div > input::placeholder { color:#475569 !important; }
    .stTextInput label { color:#94a3b8 !important; font-weight:500 !important; }

    /* === Buttons === */
    .stButton > button {
        background: linear-gradient(135deg,#6366f1,#8b5cf6) !important; color:white !important;
        border:none !important; border-radius:12px !important; padding:12px 24px !important;
        font-weight:600 !important; font-size:1rem !important; transition:all 0.3s ease !important;
        box-shadow:0 4px 15px rgba(99,102,241,0.3) !important;
    }
    .stButton > button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 25px rgba(99,102,241,0.4) !important; }

    /* === Sidebar === */
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#0f172a,#1e1b4b) !important; border-right:1px solid var(--glass-border) !important; }
    [data-testid="stSidebar"] * { color:#e2e8f0 !important; }

    /* === Tabs === */
    .stTabs [data-baseweb="tab-list"] { background:rgba(15,23,42,0.6) !important; border-radius:16px !important; padding:6px !important; border:1px solid var(--glass-border) !important; }
    .stTabs [data-baseweb="tab"] { border-radius:12px !important; color:#94a3b8 !important; font-weight:500 !important; transition:all 0.3s ease !important; }
    .stTabs [aria-selected="true"] { background:rgba(99,102,241,0.15) !important; color:#a5b4fc !important; }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none !important; }

    /* === Text Area === */
    .stTextArea textarea { background:rgba(15,23,42,0.6) !important; border:1px solid rgba(99,102,241,0.2) !important; border-radius:12px !important; color:#f1f5f9 !important; }
    .stTextArea textarea:focus { border-color:#6366f1 !important; box-shadow:0 0 0 3px rgba(99,102,241,0.15) !important; }

    /* === File Uploader === */
    [data-testid="stFileUploader"] { background:rgba(15,23,42,0.4) !important; border:2px dashed rgba(99,102,241,0.3) !important; border-radius:16px !important; }

    /* === Chat === */
    [data-testid="stChatMessage"] { background:rgba(15,23,42,0.4) !important; border:1px solid rgba(99,102,241,0.1) !important; border-radius:16px !important; animation:fadeInUp 0.4s ease-out; }

    /* === Containers === */
    div[data-testid="stContainer"] { background:rgba(15,23,42,0.4) !important; border:1px solid var(--glass-border) !important; border-radius:16px !important; transition:all 0.3s ease !important; }
    div[data-testid="stContainer"]:hover { border-color:rgba(99,102,241,0.25) !important; box-shadow:0 8px 32px rgba(0,0,0,0.3) !important; }

    /* === Text Colors === */
    .main h1,.main h2,.main h3,.main h4,.main p { color:#f1f5f9 !important; }
    .main .stMarkdown { color:#cbd5e1 !important; }

    /* === Alerts === */
    .stAlert { background:rgba(15,23,42,0.6) !important; border:1px solid rgba(99,102,241,0.2) !important; border-radius:12px !important; }

    /* === Custom Classes === */
    .gradient-text { background:linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
    .hero-title { font-size:3.2rem; font-weight:900; line-height:1.1; margin-bottom:1rem; animation:fadeInUp 1s ease-out 0.5s both; }
    .hero-sub { font-size:1.15rem; color:#94a3b8; line-height:1.6; animation:fadeInUp 1s ease-out 0.7s both; }
    .auth-card { background:rgba(15,23,42,0.8); backdrop-filter:blur(20px); border:1px solid rgba(99,102,241,0.2); border-radius:24px; padding:2.5rem; animation:fadeInUp 0.8s ease-out 0.2s both; box-shadow:0 25px 50px rgba(0,0,0,0.5); }
    .auth-card:hover { border-color:rgba(99,102,241,0.4); transition:all 0.4s ease; }
    .auth-title { font-size:1.8rem; font-weight:700; color:#f1f5f9; text-align:center; margin-bottom:0.3rem; }
    .auth-sub { font-size:0.95rem; color:#64748b; text-align:center; margin-bottom:1.5rem; }
    .feature-pill { display:inline-flex; align-items:center; gap:8px; background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.2); border-radius:100px; padding:8px 18px; font-size:0.85rem; color:#a5b4fc; margin:4px; transition:all 0.3s ease; animation:scaleIn 0.5s ease-out both; }
    .feature-pill:hover { background:rgba(99,102,241,0.2); transform:translateY(-2px); }
    .metric-card { background:rgba(15,23,42,0.6); border:1px solid var(--glass-border); border-radius:16px; padding:1.5rem; text-align:center; transition:all 0.3s ease; animation:fadeInUp 0.6s ease-out both; }
    .metric-card:hover { transform:translateY(-4px); border-color:rgba(99,102,241,0.3); box-shadow:0 12px 40px rgba(0,0,0,0.3); }
    .metric-icon { font-size:2rem; margin-bottom:0.5rem; animation:float 3s ease-in-out infinite; }
    .metric-val { font-size:1.8rem; font-weight:800; }
    .metric-lbl { font-size:0.85rem; color:#64748b; margin-top:0.3rem; }
    .user-card { background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.2); border-radius:16px; padding:1.2rem; text-align:center; margin-bottom:1rem; animation:glow 3s ease-in-out infinite; }
    .user-avatar { width:60px; height:60px; border-radius:50%; background:linear-gradient(135deg,#6366f1,#ec4899); display:flex; align-items:center; justify-content:center; font-size:1.5rem; margin:0 auto 0.8rem; }

    /* === Scrollbar === */
    ::-webkit-scrollbar { width:6px; }
    ::-webkit-scrollbar-track { background:transparent; }
    ::-webkit-scrollbar-thumb { background:rgba(99,102,241,0.3); border-radius:3px; }

    /* === Link Buttons === */
    .stLinkButton > a { background:linear-gradient(135deg,#6366f1,#8b5cf6) !important; color:white !important; border:none !important; border-radius:12px !important; }

    /* === Radio Horizontal Pills === */
    .stRadio > div { gap:0 !important; }
    .stRadio [role="radiogroup"] { gap:0.5rem !important; }
    .stRadio label { background:rgba(15,23,42,0.5) !important; border:1px solid rgba(99,102,241,0.15) !important; border-radius:12px !important; padding:10px 24px !important; color:#94a3b8 !important; transition:all 0.3s ease !important; }
    .stRadio label[data-checked="true"], .stRadio label:has(input:checked) { background:rgba(99,102,241,0.2) !important; border-color:rgba(99,102,241,0.5) !important; color:#a5b4fc !important; }
    </style>
    <div class="bg-orbs"><div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div></div>
    """)

# ==========================================
# LOGIN PAGE
# ==========================================
def show_login_page():
    st.markdown("<br>", unsafe_allow_html=True)
    hero_col, _, form_col = st.columns([1.2, 0.1, 1])

    with hero_col:
        st.markdown("""
        <div style="animation:slideInLeft 1s ease-out 0.3s both;">
            <span style="font-size:0.9rem; color:#818cf8; font-weight:600; letter-spacing:2px; text-transform:uppercase;">
                ✨ AI-Powered Career Platform
            </span>
            <h1 class="hero-title"><span class="gradient-text">Your AI<br>Career<br>Co-Pilot</span></h1>
            <p class="hero-sub">
                Leverage artificial intelligence to analyze your resume,
                discover dream jobs, and get personalized career coaching.
            </p>
            <br>
            <div style="animation:fadeInUp 1s ease-out 0.9s both;">
                <span class="feature-pill">🔍 Smart Resume Analysis</span>
                <span class="feature-pill">👔 AI Job Matching</span>
                <span class="feature-pill">💬 Career Chatbot</span>
                <span class="feature-pill">⚡ Powered by Groq</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        lottie = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_kkflmtur.json")
        if lottie:
            st_lottie(lottie, height=220, key="hero_anim")

    with form_col:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        auth_mode = st.radio("Mode", ["🔐 Login", "📝 Sign Up"], horizontal=True, label_visibility="collapsed")

        if auth_mode == "🔐 Login":
            st.markdown('<p class="auth-title">Welcome Back</p>', unsafe_allow_html=True)
            st.markdown('<p class="auth-sub">Sign in to continue your career journey</p>', unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Sign In →", use_container_width=True)
                if submit:
                    username_clean = username.strip()
                    password_clean = password.strip()
                    if not username_clean or not password_clean:
                        st.error("Please fill in all fields")
                    elif authenticate(username_clean, password_clean):
                        st.session_state.authenticated = True
                        st.session_state.current_user = username_clean
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
        else:
            st.markdown('<p class="auth-title">Create Account</p>', unsafe_allow_html=True)
            st.markdown('<p class="auth-sub">Start your AI-powered career journey</p>', unsafe_allow_html=True)
            with st.form("signup_form", clear_on_submit=True):
                new_user = st.text_input("Username", placeholder="Choose a username")
                new_email = st.text_input("Email", placeholder="your@email.com")
                new_pw = st.text_input("Password", type="password", placeholder="Create a strong password")
                confirm_pw = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                agree = st.checkbox("I agree to the Terms of Service")
                submit = st.form_submit_button("Create Account →", use_container_width=True)
                if submit:
                    new_user_clean = new_user.strip()
                    new_pw_clean = new_pw.strip()
                    confirm_pw_clean = confirm_pw.strip()
                    new_email_clean = new_email.strip()
                    
                    if not all([new_user_clean, new_email_clean, new_pw_clean, confirm_pw_clean]):
                        st.error("Please fill in all fields")
                    elif new_pw_clean != confirm_pw_clean:
                        st.error("❌ Passwords do not match")
                    elif len(new_pw_clean) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    elif not agree:
                        st.error("❌ Please agree to the Terms of Service")
                    else:
                        ok, msg = register_user(new_user_clean, new_email_clean, new_pw_clean)
                        if ok:
                            st.success(f"✅ {msg} Please log in.")
                            st.balloons()
                        else:
                            st.error(f"❌ {msg}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-top:3rem; animation:fadeIn 1.5s ease-out 1.5s both;">
        <p style="color:#475569; font-size:0.8rem;">
            Powered by <span class="gradient-text" style="font-weight:600;">Groq AI</span> ·
            Built with <span style="color:#ec4899;">♥</span> using Streamlit
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# MAIN APP
# ==========================================
def show_main_app():
    with st.sidebar:
        initial = st.session_state.current_user[0].upper()
        st.markdown(f"""
        <div class="user-card">
            <div class="user-avatar">{initial}</div>
            <div style="font-weight:600; font-size:1.1rem; color:#f1f5f9;">{st.session_state.current_user}</div>
            <div style="color:#64748b; font-size:0.8rem; margin-top:4px;">🟢 Online</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 📄 Upload Resume")
        resume_file = st.file_uploader("Upload resume (PDF/DOCX)", type=['pdf', 'docx'], label_visibility="collapsed")
        if resume_file:
            with st.spinner("Parsing..."):
                st.session_state.resume_text = read_pdf(resume_file) if resume_file.type == "application/pdf" else read_docx(resume_file)
                all_skills = load_skills()
                st.session_state.resume_skills = [s for s in all_skills if s.lower() in st.session_state.resume_text.lower()]
            st.success("✅ Resume uploaded!")
            if st.session_state.resume_skills:
                st.info(f"**Skills:** {', '.join(st.session_state.resume_skills)}")
        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            for k in ["authenticated", "current_user", "resume_text", "resume_skills", "chat_messages"]:
                st.session_state[k] = "" if isinstance(st.session_state[k], str) else ([] if isinstance(st.session_state[k], list) else False)
            st.rerun()

    # Header
    st.markdown("""
    <div style="text-align:center; animation:fadeInUp 0.6s ease-out;">
        <h1 style="font-size:2.5rem; font-weight:800;"><span class="gradient-text">🚀 AI Career Co-Pilot</span></h1>
        <p style="color:#64748b; margin-top:-10px;">Your intelligent companion for career growth</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    if st.session_state.resume_text:
        wc = len(st.session_state.resume_text.split())
        sc = len(st.session_state.resume_skills)
        cols = st.columns(4)
        for i, (icon, val, lbl) in enumerate([("📄", wc, "Words"), ("🛠️", sc, "Skills"), ("🤖", "Groq", "AI Engine"), ("⚡", "Live", "Status")]):
            with cols[i]:
                st.markdown(f'<div class="metric-card" style="animation-delay:{i*0.1}s;"><div class="metric-icon">{icon}</div><div class="metric-val"><span class="gradient-text">{val}</span></div><div class="metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Resume Analyzer", "👔 Job Recommender", "💬 Career Chatbot"])

    with tab1:
        st.markdown('<div style="text-align:center;animation:fadeInUp 0.5s ease-out;"><h3><span class="gradient-text">Resume Analysis Engine</span></h3><p style="color:#64748b;">Paste a job description to see how well your resume matches</p></div>', unsafe_allow_html=True)
        if st.session_state.resume_text:
            jd_col, analysis_col = st.columns([1, 1], gap="large")
            with jd_col:
                st.markdown("#### 📋 Job Description")
                job_description = st.text_area("JD", height=400, label_visibility="collapsed", placeholder="Paste the job description here...")
                analyze_btn = st.button("⚡ Analyze Now", type="primary", use_container_width=True)
            with analysis_col:
                st.markdown("#### 📊 AI Analysis Report")
                if analyze_btn and job_description:
                    with st.spinner("🤖 AI is analyzing..."):
                        fb = get_ai_analysis(st.session_state.resume_text, job_description)
                        if fb:
                            st.markdown(fb)
                elif analyze_btn:
                    st.warning("Please paste a job description.")
                else:
                    st.info("Your analysis report will appear here.")
        else:
            st.markdown('<div class="metric-card" style="text-align:center;padding:3rem;"><div style="font-size:3rem;margin-bottom:1rem;">📄</div><div style="font-size:1.2rem;color:#94a3b8;">Upload your resume in the sidebar to get started</div></div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div style="text-align:center;animation:fadeInUp 0.5s ease-out;"><h3><span class="gradient-text">AI Job Discovery</span></h3><p style="color:#64748b;">Let AI find the perfect opportunities for you</p></div>', unsafe_allow_html=True)
        if st.session_state.resume_text:
            st.markdown("#### ⚙️ Job Search Filters")
            role_col, exp_col = st.columns(2)
            with role_col:
                job_role = st.selectbox("� Job Role", ["AI Suggested Roles (Auto)", "Software Engineer", "Data Scientist", "Data Analyst", "Machine Learning Engineer", "Product Manager", "Full Stack Developer", "Backend Developer", "Frontend Developer", "DevOps Engineer"])
            with exp_col:
                job_experience = st.selectbox("🎓 Experience Level", ["Any", "Fresher / Entry Level", "1-3 Years", "3-5 Years", "5+ Years"])

            loc_col1, loc_col2, loc_col3 = st.columns(3)
            with loc_col1:
                country = st.selectbox("🌍 Country", ["USA", "India", "UK", "Canada", "Australia", "Germany", "Remote"])
            with loc_col2:
                state = st.text_input("🗺️ State/Province", placeholder="e.g., California")
            with loc_col3:
                city = st.text_input("🏙️ City", placeholder="e.g., San Francisco")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Find Jobs For Me", use_container_width=True):
                # Build location string
                location_parts = [p.strip() for p in [city, state, country] if p and p.strip() and p != "Remote"]
                search_location = ", ".join(location_parts) if location_parts else "Remote"
                if country == "Remote":
                    search_location = "Remote"

                with st.spinner("🤖 Generating job titles..."):
                    if job_role == "AI Suggested Roles (Auto)":
                        terms = get_job_search_terms(st.session_state.resume_text)
                        st.info(f"AI suggests: **{', '.join(terms)}**")
                    else:
                        terms = [job_role]
                        
                with st.spinner(f"🔍 Searching jobs in {search_location}..."):
                    all_jobs = []
                    for t in terms:
                        all_jobs.extend(find_jobs(t, search_location, job_experience))
                    seen, unique = set(), []
                    for j in all_jobs:
                        key = (j.get('title'), j.get('company_name'))
                        if key not in seen:
                            unique.append(j)
                            seen.add(key)
                    if unique:
                        st.success(f"Found **{len(unique)}** relevant jobs!")
                        for j in unique:
                            with st.container(border=True):
                                st.subheader(f"💼 {j.get('title')}")
                                st.write(f"**🏢** {j.get('company_name')} | **📍** {j.get('location')}")
                                with st.expander("📄 Show Description"):
                                    st.markdown(j.get('description', 'N/A'))
                                if link := j.get('related_links', [{}])[0].get('link'):
                                    st.link_button("Apply Here →", link, use_container_width=True)
                    else:
                        st.error("No jobs found. This could be due to API limits.")
        else:
            st.markdown('<div class="metric-card" style="text-align:center;padding:3rem;"><div style="font-size:3rem;margin-bottom:1rem;">👔</div><div style="font-size:1.2rem;color:#94a3b8;">Upload your resume to discover opportunities</div></div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div style="text-align:center;animation:fadeInUp 0.5s ease-out;"><h3><span class="gradient-text">AI Career Coach</span></h3><p style="color:#64748b;">Get personalized career advice</p></div>', unsafe_allow_html=True)
        if st.session_state.resume_text:
            chat_box = st.container(height=400)
            for msg in st.session_state.chat_messages:
                with chat_box:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
            if prompt := st.chat_input("Ask me anything about your career..."):
                st.session_state.chat_messages.append({"role": "user", "content": prompt})
                with chat_box:
                    with st.chat_message("user"):
                        st.markdown(prompt)
                with chat_box:
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            full = f"Context: User's resume:\n{st.session_state.resume_text}\n\nQuestion: {prompt}"
                            resp = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": "system", "content": "You are a friendly career coach chatbot."}, {"role": "user", "content": full}]
                            )
                            ans = resp.choices[0].message.content
                            st.markdown(ans)
                st.session_state.chat_messages.append({"role": "assistant", "content": ans})
        else:
            st.markdown('<div class="metric-card" style="text-align:center;padding:3rem;"><div style="font-size:3rem;margin-bottom:1rem;">💬</div><div style="font-size:1.2rem;color:#94a3b8;">Upload your resume to chat with your AI coach</div></div>', unsafe_allow_html=True)

# ==========================================
# MAIN EXECUTION
# ==========================================
inject_css()
if st.session_state.authenticated:
    show_main_app()
else:
    show_login_page()