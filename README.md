# 🤖 LeetCode AI Coach

Powered by **Gemini AI** + **FastAPI** — Enter any LeetCode username to get a full performance breakdown and personalized 7-day practice plan.

---

## 📁 Project Structure

```
leetcode-ai-coach/
├── server.py          # FastAPI backend
├── main.py            # CLI version (also works)
├── leetcode.py        # LeetCode GraphQL data fetching
├── ai_coach.py        # Gemini AI analysis
├── data.json          # Auto-filled daily snapshots
├── .env               # Your Gemini API key
├── .gitignore
├── requirements.txt
└── static/
    └── index.html     # Web UI
```

---

## 🚀 Setup & Run

### 1. Create virtual environment
```bash
python -m venv venv

# Mac/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Gemini API key to `.env`
```
GEMINI_API_KEY=your_actual_key_here
```
Get a free key at: https://aistudio.google.com/app/apikey

### 4. Run the web server
```bash
python server.py
```

### 5. Open in browser
```
http://localhost:8000
```

---

## 💻 CLI Mode (alternative)
```bash
python main.py
```

---

## ✨ Features
- 📊 Live LeetCode stats (Easy / Medium / Hard solved)
- 🔥 Streak & active days tracking
- 📆 7-day activity heatmap
- 🤖 Gemini AI performance analysis
- ⚠️ Weak area identification
- 📅 Personalized 7-day practice plan
- 💾 90-day history tracking
