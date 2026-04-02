# 🚀 AI Career Co-Pilot

A sophisticated, AI-powered Streamlit application designed to be a personal career assistant. This tool helps users analyze their resumes against specific job descriptions, discovers relevant job opportunities in real-time using advanced location/role filters, and provides a conversational AI chatbot for career advice.

**Maintained and Powered by Ramya**

---

Try it out !! deployed in Streamlit cloud app
https://ramya-made-resume-analyzer.streamlit.app/

### ✨ Features

This application was completely overhauled with a modern glassmorphism UI, a secure authentication layer, and blazing-fast AI inference. It features three core modules:

**🔒 Secure User Authentication**
*   **Sign Up & Login:** A secure portal requiring users to create an account. Passwords are cryptographically hashed (SHA-256) ensuring user data is secure. 

**1. 🔍 AI-Powered Resume Analyzer**
*   **Upload and Parse:** Users can upload their resumes in PDF or DOCX format.
*   **Deep Contextual Analysis:** Performs a deep, semantic analysis of the resume against a pasted job description (with built-in validation checks to prevent AI hallucinations).
*   **Detailed Feedback:** Generates a comprehensive report including a **Match Score**, **Missing Keywords**, an **AI-written Profile Summary**, and **Actionable Advice**.

**2. 👔 Intelligent Job Recommender**
*   **Advanced AI Search:** The app uses an AI model to determine the most relevant *job titles* based on the user's resume content, or allows users to manually select from a dropdown of tech roles.
*   **Smart Location Filtering:** Cascading, dynamic dropdown menus that let you filter by **Country**, **State**, and **City** simultaneously, or select "Remote" for global listings.
*   **Experience Level Filtering:** Dropdowns for defining your background (e.g. Fresher / Entry Level) which strictly translates into the Google Jobs API format.
*   **Real-Time Data:** Integrates with the SerpApi Google Jobs API to fetch current job openings with direct application links.

**3. 💬 Conversational Career Chatbot**
*   **Pre-loaded Context:** The chatbot is pre-loaded with the structured text of the user's uploaded resume under the hood.
*   **Personalized Mentorship:** Users can ask for tailored interview prep, how to improve project descriptions, or general career mapping.

---

### 🛠️ Technology Stack

*   **Frontend UI:** Built completely in [Streamlit](https://streamlit.io/) with heavy custom CSS injections for a premium Web App feel (animations, gradients, modern typography).
*   **AI Engine (Inference):** [Groq API](https://groq.com/) for lightning-fast LPU inference speeds.
*   **LLM Model:** Meta's `llama-3.3-70b-versatile` (Replacing OpenAI).
*   **Job Search:** [SerpApi Google Jobs API](https://serpapi.com/)
*   **Core Systems:** Python 3.9+, `PyPDF2`, `python-docx`, `hashlib`

---

### 🚀 Setup and Installation

Follow these steps to get the application running on your local machine.

**1. Clone the Repository**
```bash
git clone https://github.com/Ramyashree-20/resume-analyzer-nlp
cd resume-analyzer-nlp
```

**2. Create and activate a virtual environment:**
*   **Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
*   **macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

**3. Install the required dependencies:**
Run the following to install all necessary packages (Streamlit, Groq, SerpApi, etc.):
```bash
pip install -r requirements.txt
```

**4. Set up your API Keys:**
*   Create a folder named `.streamlit` in the root of your project directory.
*   Inside the `.streamlit` folder, create a file named `secrets.toml`.
*   Add your API keys to the `secrets.toml` file matching this format EXACTLY:
    ```toml
    GROQ_API_KEY = "gsk_YourSecretGroqKeyHere"
    SERPAPI_API_KEY = "YourSecretSerpApiKeyHere"
    ```

### 💻 Running the Application

Once the setup is complete, spin up the server with the following command:
```bash
streamlit run app.py
```
> The application will open in your browser natively at `http://localhost:8501`. Create an account on the splash page to enter the dashboard!
