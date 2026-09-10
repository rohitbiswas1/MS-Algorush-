from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import uvicorn

load_dotenv()

from leetcode import (
    fetch_leetcode_stats,
    save_daily_snapshot,
    load_history,
    calculate_progress,
)

from ai_coach import (
    analyze_with_gemini,
    extract_sections,
    get_gemini_client,
)

app = FastAPI(title="LeetCode AI Coach")


# =========================================================
# REQUEST MODELS
# =========================================================

class UsernameRequest(BaseModel):
    username: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


# =========================================================
# API: STATS
# =========================================================

@app.post("/api/stats")
async def get_stats(body: UsernameRequest):
    username = body.username.strip()

    if not username:
        return {
            "error": "Username is required"
        }

    try:
        stats = fetch_leetcode_stats(username)

        if not stats:
            return {
                "error": f"User '{username}' not found on LeetCode"
            }

        save_daily_snapshot(stats)

        history = load_history(username)

        progress = calculate_progress(history)

        return {
            "stats": stats,
            "progress": progress,
            "history": history[-7:],
        }

    except Exception as e:
        return {
            "error": f"Failed to fetch stats: {str(e)}"
        }


# =========================================================
# API: GEMINI ANALYSIS
# =========================================================

@app.post("/api/analyze")
async def get_analysis(body: UsernameRequest):
    username = body.username.strip()

    if not username:
        return {
            "error": "Username is required"
        }

    try:
        stats = fetch_leetcode_stats(username)

        if not stats:
            return {
                "error": f"User '{username}' not found on LeetCode"
            }

        history = load_history(username)

        progress = calculate_progress(history)

        ai_response = analyze_with_gemini(
            stats,
            history,
            progress
        )

        sections = extract_sections(ai_response)

        return {
            "analysis": sections["analysis"],
            "weak_areas": sections["weak_areas"],
            "next_action": sections.get(
                "next_action",
                ""
            ),
            "practice_plan": sections["practice_plan"],
            "motivation": sections.get(
                "motivation",
                ""
            ),
            "raw": sections["raw"],
        }

    except Exception as e:
        return {
            "error": f"Gemini analysis failed: {str(e)}"
        }


# =========================================================
# API: AI CHAT
# =========================================================

@app.post("/api/chat")
async def chat(body: ChatRequest):

    message = body.message.strip()

    if not message:
        return {
            "reply": "Please enter a message."
        }

    try:
        client = get_gemini_client()

        history_text = ""

        # Keep only the last 10 messages
        for item in body.history[-10:]:

            role = (
                "User"
                if item.role.lower() == "user"
                else "Assistant"
            )

            history_text += (
                f"{role}: {item.content}\n"
            )

        prompt = f"""
You are the LeetCode AI Coach.

You specialize in:
- DSA
- Algorithms
- Data structures
- LeetCode
- Competitive programming
- Coding interview preparation
- Time and space complexity

Be concise, clear, practical, and friendly.

Conversation so far:
{history_text}

User:
{message}

Answer the user directly.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        if not response or not response.text:
            return {
                "reply": "Gemini returned an empty response."
            }

        return {
            "reply": response.text
        }

    except Exception as e:

        error_text = str(e)

        if (
            "API_KEY_INVALID" in error_text
            or "API key not valid" in error_text
        ):
            return {
                "reply": (
                    "Gemini API key is invalid. "
                    "Please update your GEMINI_API_KEY "
                    "in the .env file."
                )
            }

        return {
            "reply": f"Gemini error: {error_text}"
        }


# =========================================================
# STATIC FRONTEND
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


@app.get("/")
async def root():
    return FileResponse(
        "static/index.html"
    )


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )