# 🤖 AI Career Co-Pilot

A sophisticated, AI-powered Streamlit application designed to be a personal career assistant. This tool helps users analyze their resumes against specific job descriptions, discovers relevant job opportunities in real-time, and provides a conversational AI chatbot for career advice.

---

Try it out !!
https://ramya-made-resume-analyzer.streamlit.app/

### ✨ Features

This application is built with three core modules, accessible through a clean, tab-based interface:

**1. 🔍 AI-Powered Resume Analyzer**
*   **Upload and Parse:** Users can upload their resumes in PDF or DOCX format.
*   **Deep Contextual Analysis:** Instead of simple keyword matching, the app uses OpenAI's GPT models to perform a deep, semantic analysis of the resume against a pasted job description.
*   **Detailed Feedback:** The analysis generates a comprehensive report including:
    *   A **Match Score** with a clear justification.
    *   A list of **Missing Keywords** and skills.
    *   An improved, AI-written **Profile Summary** tailored for the job.
    *   **Actionable Advice** on how to enhance the resume.

**2. 👔 Intelligent Job Recommender**
*   **AI-Driven Search:** The app doesn't just search for a list of skills. It uses an AI model to determine the most relevant *job titles* based on the user's resume content.
*   **Real-Time Job Listings:** It integrates with the SerpApi Google Jobs API to fetch current job openings based on the AI-suggested titles.
*   **Direct Apply Links:** Each job listing includes the company, location, a brief description, and a direct link to the application page.

**3. 💬 Conversational Career Chatbot**
*   **Context-Aware:** The chatbot is pre-loaded with the context of the user's uploaded resume.
*   **Personalized Advice:** Users can ask specific questions about their resume ("How can I improve my project descriptions?") or general career questions ("What are the career paths for a data analyst?").
*   **Interactive and Engaging:** Provides a familiar chat interface for a natural and helpful conversation.

---

### 🛠️ Technology Stack

*   **Frontend:** [Streamlit](https://streamlit.io/)
*   **AI & NLP:** [OpenAI API (GPT-4o mini)](https://openai.com/)
*   **Job Search:** [SerpApi Google Jobs API](https://serpapi.com/)
*   **File Parsing:** `PyPDF2`, `python-docx`
*   **Core Language:** Python 3.9+

---

### 🚀 Setup and Installation

Follow these steps to get the application running on your local machine.

**1. Clone the Repository**
```bash
git clone https://github.com/Ramyashree-20/resume-analyzer-nlp` 

---

2.  **Create and activate a virtual environment:**
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

3.  **Install the required dependencies:**
    Create a `requirements.txt` file with the content below, then run `pip install -r requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API Keys:**
    *   Create a folder named `.streamlit` in the root of your project directory.
    *   Inside the `.streamlit` folder, create a file named `secrets.toml`.
    *   Add your API keys to the `secrets.toml` file like this:
        ```toml
        OPENAI_API_KEY = "sk-YourSecretOpenAIKeyHere"
        SERPAPI_API_KEY = "YourSecretSerpApiKeyHere"
        ```

### Running the Application

Once the setup is complete, run the following command in your terminal:
```bash
streamlit run app.py
