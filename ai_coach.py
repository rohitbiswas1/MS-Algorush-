import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# Current Gemini Flash model documented by Google.
MODEL = "gemini-3.7-flash"
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)


def _get_api_key() -> str:
    api_key = (os.getenv("GEMINI_API_KEY") or "").strip().strip('"\'')
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. Add a valid key to the project's .env file."
        )
    return api_key


def get_gemini_client() -> genai.Client:
    """Create a fresh Gemini client.

    Callers that use this compatibility helper should close the returned client
    after the request. New request code should prefer _generate_with_gemini().
    """
    return genai.Client(api_key=_get_api_key())


def _generate_with_gemini(contents: str):
    """Generate one response with a request-scoped client.

    The google-genai SDK uses an underlying HTTP client. In serverless/FastAPI
    environments, reusing a client after its transport has been cleaned up can
    produce: "Cannot send a request, as the client has been closed."
    A context-managed client guarantees the request finishes before cleanup.
    """
    with genai.Client(api_key=_get_api_key()) as client:
        return client.models.generate_content(
            model=MODEL,
            contents=contents,
        )


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
    if "client has been closed" in error_text.lower():
        return "Gemini connection was closed before the request completed. Please retry; the app now uses a request-scoped Gemini client."
    return f"Gemini error: {error_text}"


def analyze_with_gemini(stats: dict, history: list[dict], progress: dict) -> str:
    try:
        response = _generate_with_gemini(
            build_prompt(stats, history, progress)
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
