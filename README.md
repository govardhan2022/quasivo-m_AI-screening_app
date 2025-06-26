🌟 Features
✅ Upload PDF resumes and job descriptions
💬 Generate 3 custom interview questions
🎯 Get AI-generated scores + explanations
💾 Save results locally as JSON files
🔐 Static login for reviewer authentication (bonus)
🗣️ Voice input support (bonus)
📁 External Gemini prompt templates in /prompts/ (submission requirement)
🖥️ Runs entirely locally – no cloud storage or deployment needed


📂 data/ – Local Results Storage
All completed screenings are saved here as timestamped JSON files like:



1
screening_20250428_143045.json
Each file contains:

Job Description
Candidate Resume
Interview Questions
Candidate Answers
Scores & Explanations
Timestamp
📂 prompts/ – Gemini Prompt Templates
Contains prompt strings used with the Gemini API:

generate_questions.txt: For generating interview questions
score_answer.txt: For scoring answers
🛠️ Technologies Used
TECHNOLOGY
PURPOSE
Streamlit
Web interface framework
Google Gemini API
Generate questions & score answers
PyPDF2
Extract text from uploaded résumés
SpeechRecognition
Voice-to-text input for answering questions
Python-dotenv
Secure handling of API keys
JSON
Local storage format for results

🤝 Contributing
Contributions are welcome! If you'd like to improve this project, please follow these steps:

Fork the repo
Create your feature branch (git checkout -b feature/new-feature)
Commit your changes (git commit -m "Add new feature")
Push to the branch (git push origin feature/new-feature)
Open a Pull Request
📄 License
This project is licensed under the MIT License – see the LICENSE file for details.

# 🤖 Quasivo AI Screening App

[![Build](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/quasivo-ai-screening) 
[![License](https://img.shields.io/github/license/yourusername/quasivo-ai-screening)](LICENSE) 
[![Python](https://img.shields.io/badge/python-3.9+-blue)](https://www.python.org/) 
[![Streamlit](https://img.shields.io/badge/framework-streamlit-orange)](https://streamlit.io) 

A Streamlit-based interview assistant powered by **Google Gemini API**, designed to generate interview questions and evaluate candidate responses using AI.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [How to Run the App Locally](#how-to-run-the-app-locally)
4. [Folder Structure and Data Storage](#folder-structure-and-data-storage)
5. [Contributing](#contributing)
6. [License](#license)

---

## 🧠 Overview

This app helps hiring teams screen job candidates by:
- Generating tailored interview questions based on a job description and resume.
- Evaluating answers using Google Gemini's powerful LLM capabilities.
- Providing instant feedback and scoring (1–10) per question.

Perfect for recruiters, HR teams, and technical leads who want to streamline their screening process with AI.

---

## 🌟 Features

- ✅ Upload PDF resumes and job descriptions
- 💬 Generate 3 custom interview questions
- 🎯 Get AI-generated scores + explanations
- 💾 Save results locally as JSON files
- 🌐 Built with Streamlit — fast, responsive UI

---

## 🚀 How to Run the App Locally

### ✅ Prerequisites

Before running the app, ensure you have the following installed:

- Python 3.9+
- `pip` (Python package installer)
- A Google Gemini API key ([Get one here](https://makersuite.google.com/)) 

---

### 📦 Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/quasivo-ai-screening.git 
   cd quasivo-ai-screening