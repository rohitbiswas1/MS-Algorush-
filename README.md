# 🤖 LeetMind

> **Your AI-powered personal learning & performance coach**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-LeetMind-blue?style=for-the-badge)](https://leet-mind.vercel.app/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-AI-8E75B2?logo=google)](https://ai.google.dev/)

## 🌐 Live Demo

### [🚀 Open LeetMind](https://leet-mind.vercel.app/)

**Live:** https://leet-mind.vercel.app/

LeetMind is an AI-powered personal learning and performance coach that combines user activity data with **Google Gemini AI** to turn progress into actionable insights, recommendations, and personalized learning plans. The current release includes **LeetCode integration** for coding-progress analysis, while the platform is designed to support broader learning and performance-coaching use cases.

---

## ✨ Key Features

- 📊 **Interactive Progress Dashboard** — View profile, ranking, solved problems, activity, streaks, and progress in one place.
- 🔗 **LeetCode GraphQL Integration** — Fetch public LeetCode statistics and recent submission activity automatically.
- 🤖 **Gemini AI Analysis** — Convert user data into useful performance insights.
- 🎯 **Improvement Guidance** — Identify areas that need more attention and turn them into practical next steps.
- 📚 **Personalized Practice Plans** — Generate structured 7-day improvement plans.
- 💬 **Interactive AI Assistant** — Ask questions and receive guidance from the LeetMind AI Coach.
- 📈 **Progress Tracking** — Save snapshots and compare progress over time.
- 🌙 **Responsive UI + Theme Toggle** — Clean dashboard and chat experience with light/dark mode.
- 🛡️ **Environment-based API Key Security** — Gemini credentials are loaded through environment variables rather than hard-coded.

---

## 🧠 How Gemini Is Used

Google Gemini is the intelligence layer of LeetMind. It is used to:

1. Analyze user progress and activity data.
2. Generate performance insights.
3. Highlight potential areas for improvement.
4. Create actionable learning and practice plans.
5. Power the interactive AI assistant.

For the current coding-focused workflow, Gemini receives relevant LeetCode statistics and activity context and converts them into personalized coaching.

---

## 🔗 LeetCode GraphQL Integration

LeetMind uses LeetCode's GraphQL endpoint to retrieve public user statistics:

```text
https://leetcode.com/graphql
```

The integration fetches information such as username, ranking, solved-problem counts, streak, active days, and recent submission activity.

---

## 🛠️ Tech Stack

- **Python** — application and backend logic
- **FastAPI** — backend API and web server
- **HTML / CSS / JavaScript** — frontend interface
- **Google Gemini API** — AI analysis and chat
- **LeetCode GraphQL API** — public coding statistics
- **Requests** — API communication
- **JSON** — progress snapshots and history
- **Vercel** — production deployment

---

## 📁 Project Structure

```text
LeetMind/
├── server.py          # FastAPI backend and API routes
├── leetcode.py        # LeetCode GraphQL integration and history
├── ai_coach.py        # Gemini AI analysis and chat logic
├── main.py            # Optional CLI interface
├── requirements.txt   # Python dependencies
├── vercel.json        # Vercel configuration
├── .gitignore
└── static/
    └── index.html     # Dashboard and AI chat UI
```

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/rohitbiswas1/LeetMind.git
cd LeetMind
```

### 2. Create and activate a virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Never commit your real API key to GitHub.

### 5. Start the application

```bash
python server.py
```

Open:

```text
http://localhost:8000
```

---

## 🔐 Deployment

LeetMind is deployed on Vercel.

Set this environment variable in Vercel:

```text
GEMINI_API_KEY
```

The Gemini integration also includes retry/backoff handling and fallback models for temporary service-capacity or rate-limit errors.

---

## 🎯 Why LeetMind?

Raw progress data tells you **what happened**, but not always **what you should do next**. LeetMind adds an AI coaching layer that turns activity and performance data into clear, actionable guidance.

---

## 📌 Current Focus

The current version is especially useful for **LeetCode and DSA learners**, while the architecture is intentionally designed to expand into additional learning, productivity, and performance use cases.

---

## 🏆 Project Achievement

LeetMind was built as a **solo project** for the **ML AlgoRush AI Chatbot Development Challenge** and secured **3rd place**.

---

## 🔗 Links

- 🌐 **Live Demo:** https://leet-mind.vercel.app/
- 💻 **GitHub:** https://github.com/rohitbiswas1/LeetMind
