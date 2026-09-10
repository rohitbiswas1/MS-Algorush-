import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


MODEL = "gemini-3.6-flash"
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)


def get_gemini_client() -> genai.Client:
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip().strip('"\'')
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add a valid key to the project's .env file."
        )
    return genai.Client(api_key=api_key)


def build_prompt(stats: dict, history: list[dict], progress: dict) -> str:
    solved = stats["solved"]
    recent_summary = "\n".join(
        f"  {day['date']}: {day['submissions']} submission(s)"
        for day in stats.get("recent_7_days", [])
    )
    history_summary = "\n".join(
        f"  {entry['date']}: {entry['stats']['solved']['total']} solved"
        for entry in history[-5:]
    ) or "Not enough history yet for trend analysis."
    return f"""
You are an expert LeetCode coach helping a student improve their competitive programming skills.

USERNAME: {stats['username']}
GLOBAL RANKING: {stats.get('ranking', 'Unknown')}
STREAK: {stats.get('streak', 0)} days

PROBLEMS SOLVED:
- Easy: {solved['easy']}
- Medium: {solved['medium']}
- Hard: {solved['hard']}
- Total: {solved['total']}

PROGRESS SINCE LAST SESSION:
- New Easy: {progress.get('new_easy', 0)}
- New Medium: {progress.get('new_medium', 0)}
- New Hard: {progress.get('new_hard', 0)}
- New Total: {progress.get('new_total', 0)}

ACTIVITY LAST 7 DAYS:
{recent_summary}

HISTORICAL GROWTH:
{history_summary}

Provide these headers exactly:
### PERFORMANCE ANALYSIS
### WEAK AREAS
### NEXT ACTION
### 7-DAY PRACTICE PLAN
### MOTIVATION

Keep the advice encouraging, honest, and practical.
"""


def _format_gemini_error(error: Exception) -> str:
    error_text = str(error)
    if "API_KEY_INVALID" in error_text or "API key not valid" in error_text:
        return "Gemini API key is invalid. Replace GEMINI_API_KEY in .env or Vercel Environment Variables and restart/redeploy the app."
    return f"Gemini error: {error_text}"


def analyze_with_gemini(stats: dict, history: list[dict], progress: dict) -> str:
    try:
        response = get_gemini_client().models.generate_content(
            model=MODEL,
            contents=build_prompt(stats, history, progress),
        )
        return response.text or "Gemini returned an empty response."
    except Exception as error:
        return _format_gemini_error(error)


def ask_coach(question: str, stats: dict, history: list[dict]) -> str:
    history_text = "\n".join(
        f"{'User' if item.get('role') == 'user' else 'Assistant'}: {item.get('content', '')}"
        for item in history[-10:]
    )
    prompt = f"""
You are the LeetCode AI Coach. Give concise, clear, practical help with DSA,
algorithms, LeetCode, competitive programming, and coding interviews.

Student profile: {stats}
Conversation:
{history_text}

User question: {question}
Answer directly and include complexity when relevant.
"""
    try:
        response = get_gemini_client().models.generate_content(
            model=MODEL,
            contents=prompt,
        )
        return response.text or "Gemini returned an empty response."
    except Exception as error:
        return _format_gemini_error(error)


def extract_sections(ai_response: str) -> dict:
    sections = {
        "analysis": "",
        "weak_areas": "",
        "next_action": "",
        "practice_plan": "",
        "motivation": "",
        "raw": ai_response,
    }
    headings = {
        "performance analysis": "analysis",
        "weak areas": "weak_areas",
        "next action": "next_action",
        "practice plan": "practice_plan",
        "motivation": "motivation",
    }
    current = None
    buffer = []
    for line in ai_response.splitlines():
        heading = next((key for key in headings if key in line.lower()), None)
        if heading:
            if current:
                sections[current] = "\n".join(buffer).strip()
            current = headings[heading]
            buffer = []
        elif current:
            buffer.append(line)
    if current:
        sections[current] = "\n".join(buffer).strip()
    return sections
