import os
import random
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai


MODEL = "gemini-3.6-flash"
FALLBACK_MODELS = ["gemini-3.7-flash", "gemini-2.5-flash"]
MAX_ATTEMPTS_PER_MODEL = 2

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)


def _get_api_key() -> str:
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip().strip('"\'')
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add a valid key to the project's .env file."
        )
    return api_key


def get_gemini_client() -> genai.Client:
    return genai.Client(api_key=_get_api_key())


def _is_transient_error(error: Exception) -> bool:
    text = str(error).lower()
    return any(marker in text for marker in (
        "503", "unavailable", "high demand", "temporarily overloaded",
        "429", "resource_exhausted", "rate limit", "too many requests",
    ))


def _generate_with_gemini(contents: str):
    """Generate with exponential backoff and fallback Gemini models."""
    models = [MODEL] + [m for m in FALLBACK_MODELS if m != MODEL]
    last_error = None

    for model_index, model in enumerate(models):
        for attempt in range(MAX_ATTEMPTS_PER_MODEL):
            try:
                # Request-scoped client prevents stale/closed HTTP transports.
                with genai.Client(api_key=_get_api_key()) as client:
                    return client.models.generate_content(
                        model=model,
                        contents=contents,
                    )
            except Exception as error:
                last_error = error
                if not _is_transient_error(error):
                    raise
                delay = min(2 ** attempt, 4) + random.uniform(0, 0.5)
                time.sleep(delay)

        if model_index < len(models) - 1:
            time.sleep(0.5)

    raise last_error or RuntimeError("Gemini request failed.")


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
    lower = error_text.lower()
    if "api_key_invalid" in lower or "api key not valid" in lower:
        return "Gemini API key is invalid. Replace GEMINI_API_KEY in .env or Vercel Environment Variables and restart/redeploy the app."
    if "client has been closed" in lower:
        return "Gemini connection was closed before the request completed. Please retry; LeetMind now uses a request-scoped client."
    if "503" in lower or "unavailable" in lower or "high demand" in lower:
        return "Gemini is temporarily busy. LeetMind automatically retries and switches to a fallback Gemini model. Please try again in a few seconds."
    if "429" in lower or "resource_exhausted" in lower or "rate limit" in lower:
        return "Gemini rate limit reached. LeetMind automatically retries with backoff and a fallback model. Please try again shortly."
    return f"Gemini error: {error_text}"


def analyze_with_gemini(stats: dict, history: list[dict], progress: dict) -> str:
    try:
        response = _generate_with_gemini(build_prompt(stats, history, progress))
        return response.text or "Gemini returned an empty response."
    except Exception as error:
        return _format_gemini_error(error)


def ask_coach(question: str, stats: dict, history: list[dict]) -> str:
    history_text = "\n".join(
        f"{'User' if item.get('role') == 'user' else 'Assistant'}: {item.get('content', '')}"
        for item in history[-10:]
    )
    prompt = f"""
You are the LeetMind AI Coach. Give concise, clear, practical help with DSA,
algorithms, LeetCode, competitive programming, and coding interviews.

Student profile: {stats}
Conversation:
{history_text}

User question: {question}
Answer directly and include complexity when relevant.
"""
    try:
        response = _generate_with_gemini(prompt)
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
