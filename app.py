import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import datetime
import speech_recognition as sr
import pyodbc
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please check your .env file.")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)

# Configure Database Connection (Local SQL Server)
def get_db_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=CandidateScreeningDB;'
        'Trusted_Connection=yes;'
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='InterviewResults' AND xtype='U')
        CREATE TABLE InterviewResults (
            id INT IDENTITY(1,1) PRIMARY KEY,
            job_description NVARCHAR(MAX),
            resume_text NVARCHAR(MAX),
            questions NVARCHAR(MAX),
            answers NVARCHAR(MAX),
            scores NVARCHAR(MAX),
            explanations NVARCHAR(MAX),
            timestamp DATETIME
        )
    """)
    conn.commit()
    conn.close()

init_db()

class CandidateScreeningApp:
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def extract_text_from_pdf(self, pdf_file):
        try:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {e}")
            return ""

    def read_prompt(self, filename):
        with open(f"prompts/{filename}", "r", encoding="utf-8") as f:
            return f.read()

    def generate_interview_questions(self, job_description, resume_text):
        prompt_template = self.read_prompt("generate_questions.txt")
        prompt = prompt_template.format(
            job_description=job_description[:3000],
            resume_text=resume_text[:1500]
        )
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            content = response.text.strip()
            questions = [line.strip() for line in content.split('\n') if line.strip()]
            return questions[:3]
        except Exception as e:
            st.error(f"Error generating questions: {e}")
            return []

    def score_answer(self, question, answer):
        prompt_template = self.read_prompt("score_answer.txt")
        prompt = prompt_template.format(
            question=question,
            answer=answer
        )
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            content = response.text.strip()

            if content and len(content) >= 2 and content[0].isdigit():
                score = int(content[0])
                explanation = content[2:].strip()
            else:
                score = 6
                explanation = "Good attempt! The answer was somewhat clear and relevant."

            score = max(1, min(score, 10))
            return score, explanation
        except Exception as e:
            st.error(f"Error scoring answer: {e}")
            return 6, "The AI had trouble evaluating this one."

    def save_to_json(self, data):
        filename = f"screening_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(self.data_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return filename

    def save_to_sql(self, data):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            formatted_time = datetime.datetime.fromisoformat(data["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                INSERT INTO InterviewResults 
                (job_description, resume_text, questions, answers, scores, explanations, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                           json.dumps(data["job_description"]),
                           json.dumps(data["resume_text"]),
                           json.dumps(data["questions"]),
                           json.dumps(data["answers"]),
                           json.dumps(data["scores"]),
                           json.dumps(data["explanations"]),
                           formatted_time)
            conn.commit()
        except Exception as e:
            st.error(f"❌ Could not save results to database: {e}")
        finally:
            conn.close()

    def run(self):
        st.set_page_config(page_title="🤖 Quasivo AI Screening App", layout="wide")
        st.title("🤖 Quasivo AI Screening App")

        # Static Login
        if "logged_in" not in st.session_state:
            pwd = st.text_input("Enter Admin Password:", type="password")
            if st.button("Login"):
                if pwd == "admin123":
                    st.session_state.logged_in = True
                    st.experimental_rerun()
                else:
                    st.error("Invalid password.")
            return

        # Input Collection
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Job Description")
            jd_method = st.radio("Input Method", ["Text", "File"], key="jd_input")
            if jd_method == "Text":
                job_description = st.text_area("Paste job description here:", height=200, key="jd_text")
            else:
                jd_file = st.file_uploader("Upload JD (TXT or PDF)", type=["txt", "pdf"], key="jd_upload")
                job_description = ""
                if jd_file:
                    if jd_file.type == "application/pdf":
                        job_description = self.extract_text_from_pdf(jd_file)
                    else:
                        job_description = jd_file.read().decode("utf-8")
                    st.success("✅ Job description loaded successfully!")

        with col2:
            st.subheader("Candidate Resume")
            resume_input_method = st.radio("Resume input method:", ["Text Input", "File Upload"])
            if resume_input_method == "Text Input":
                resume_text = st.text_area("Paste resume here:", height=200)
            else:
                resume_file = st.file_uploader("Upload resume (PDF only)", type=["pdf"])
                if resume_file:
                    resume_text = self.extract_text_from_pdf(resume_file)
                    st.success("✅ Resume uploaded successfully!")
                else:
                    resume_text = ""

        if st.button("🚀 Start Screening") and job_description and resume_text:
            with st.spinner("🎯 Getting ready to ask some great questions..."):
                questions = self.generate_interview_questions(job_description, resume_text)
                if questions:
                    st.session_state.questions = questions
                    st.session_state.answers = {}
                    st.session_state.scores = {}
                    st.session_state.resume_text = resume_text
                    st.session_state.job_description = job_description
                    st.session_state.current_idx = 0
                    st.rerun()

        # Interview Flow
        if 'questions' in st.session_state and st.session_state.questions:
            total = len(st.session_state.questions)
            current_idx = st.session_state.get("current_idx", 0)

            st.markdown("---")
            st.subheader(f"Question {current_idx + 1} of {total}")
            question = st.session_state.questions[current_idx]
            st.markdown(f"**{question}**")

            default_answer = st.session_state.answers.get(current_idx, "")
            answer = st.text_area("Your Answer:", value=default_answer, key=f"ans_{current_idx}", height=150)

            # Voice Input Button
            if st.button("🎙️ Use Voice Input", key=f"voice_{current_idx}"):
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    st.info("🎤 Listening...")
                    audio = r.listen(source)
                    try:
                        spoken_text = r.recognize_google(audio)
                        st.session_state.answers[current_idx] = spoken_text
                        st.experimental_rerun()
                    except:
                        st.warning("⚠️ Could not understand audio.")

            col_nav = st.columns([1, 1, 1])
            with col_nav[0]:
                if current_idx > 0:
                    if st.button("⬅️ Previous", use_container_width=True):
                        st.session_state.answers[current_idx] = answer
                        st.session_state.current_idx -= 1
                        st.experimental_rerun()
            with col_nav[2]:
                if current_idx < total - 1:
                    if st.button("Next ➡️", use_container_width=True):
                        st.session_state.answers[current_idx] = answer
                        st.session_state.current_idx += 1
                        st.rerun()
                else:
                    if st.button("Finish", use_container_width=True):
                        st.session_state.answers[current_idx] = answer

                        # Score all answers
                        scores = {}
                        explanations = {}
                        for idx in range(total):
                            q = st.session_state.questions[idx]
                            a = st.session_state.answers.get(idx, "")
                            score, explanation = self.score_answer(q, a)
                            scores[idx] = score
                            explanations[idx] = explanation
                        st.session_state.scores = scores
                        st.session_state.explanations = explanations
                        st.session_state.completed = True
                        st.rerun()

        # Results View
        if st.session_state.get("completed"):
            st.markdown("---")
            st.subheader("✅ Results Summary")

            scores_list = list(st.session_state.scores.values())
            if scores_list:
                total_score = sum(scores_list)
                avg_score = round(total_score / len(scores_list), 1)
                st.markdown(f"### 📊 Average Score: **{avg_score}/10**")
            else:
                st.warning("⚠️ Could not calculate score for any question.")

            for idx, question in enumerate(st.session_state.questions):
                score = st.session_state.scores.get(idx, 6)
                explanation = st.session_state.explanations.get(idx, "The system had trouble evaluating this one.")
                answer = st.session_state.answers.get(idx, "")

                st.markdown(f"""
                <div style="border:1px solid #eee; padding:15px; margin-bottom:10px; border-radius:8px;">
                    <strong>Question {idx+1}:</strong> {question}<br><br>
                    <strong>Your Answer:</strong> {answer}<br><br>
                    <strong>Score:</strong> {score}/10<br>
                    <em>{explanation}</em>
                </div>
                """, unsafe_allow_html=True)

            col_save = st.columns([1, 1])
            with col_save[0]:
                if st.button("💾 Save to JSON"):
                    data = {
                        "job_description": st.session_state.job_description,
                        "resume_text": st.session_state.resume_text,
                        "questions": st.session_state.questions,
                        "answers": st.session_state.answers,
                        "scores": st.session_state.scores,
                        "explanations": st.session_state.explanations,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    filename = self.save_to_json(data)
                    st.success(f"Saved to `{filename}` in the `data/` folder.")
            with col_save[1]:
                if st.button("💾 Save to SQL"):
                    data = {
                        "job_description": st.session_state.job_description,
                        "resume_text": st.session_state.resume_text,
                        "questions": st.session_state.questions,
                        "answers": st.session_state.answers,
                        "scores": st.session_state.scores,
                        "explanations": st.session_state.explanations,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    self.save_to_sql(data)
                    st.success("✅ Results saved to local SQL Server.")

# Run the app
if __name__ == "__main__":
    app = CandidateScreeningApp()
    app.run()
