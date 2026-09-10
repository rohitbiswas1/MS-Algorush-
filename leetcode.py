import requests
import json
import os
from datetime import datetime

LEETCODE_API = "https://leetcode.com/graphql"

# Vercel's serverless filesystem is read-only except for /tmp.
# Keep local development using data.json, but use /tmp in Vercel.
DEFAULT_DATA_FILE = (
    "/tmp/leetmind_data.json"
    if os.getenv("VERCEL")
    else "data.json"
)

STATS_QUERY = """
query getUserStats($username: String!) {
  matchedUser(username: $username) {
    username
    profile {
      realName
      ranking
    }
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
    userCalendar {
      streak
      totalActiveDays
      submissionCalendar
    }
  }
}
"""


def fetch_leetcode_stats(username: str) -> dict | None:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://leetcode.com",
    }
    payload = {
        "query": STATS_QUERY,
        "variables": {"username": username},
    }

    try:
        response = requests.post(
            LEETCODE_API,
            json=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # GraphQL can return an HTTP 200 response with errors.
        if data.get("errors"):
            return None

        user = data.get("data", {}).get("matchedUser")
        if not user:
            return None

        submissions = user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
        counts = {
            item.get("difficulty"): item.get("count", 0)
            for item in submissions
        }

        profile = user.get("profile") or {}
        calendar = user.get("userCalendar") or {}
        streak = calendar.get("streak", 0)
        total_active_days = calendar.get("totalActiveDays", 0)

        raw_calendar = calendar.get("submissionCalendar", "{}") or "{}"
        try:
            submission_map = json.loads(raw_calendar)
        except (TypeError, json.JSONDecodeError):
            submission_map = {}

        recent_days = get_recent_activity(submission_map, days=7)

        return {
            "username": user.get("username", username),
            "real_name": profile.get("realName", ""),
            "ranking": profile.get("ranking", 0),
            "solved": {
                "total": counts.get("All", 0),
                "easy": counts.get("Easy", 0),
                "medium": counts.get("Medium", 0),
                "hard": counts.get("Hard", 0),
            },
            "streak": streak,
            "total_active_days": total_active_days,
            "recent_7_days": recent_days,
            "fetched_at": datetime.now().isoformat(),
        }

    except requests.exceptions.Timeout:
        return None
    except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):
        return None


def get_recent_activity(submission_map: dict, days: int = 7) -> list[dict]:
    from datetime import timezone, timedelta

    today = datetime.now(timezone.utc).date()
    activity = []

    for i in range(days):
        day = today - timedelta(days=i)
        timestamp = str(
            int(
                datetime(
                    day.year,
                    day.month,
                    day.day,
                    tzinfo=timezone.utc,
                ).timestamp()
            )
        )
        count = submission_map.get(timestamp, 0)
        activity.append({
            "date": day.isoformat(),
            "submissions": count,
        })

    return list(reversed(activity))


def save_daily_snapshot(
    stats: dict,
    filepath: str = DEFAULT_DATA_FILE,
):
    """Save today's snapshot.

    On Vercel this uses /tmp because the deployed filesystem is read-only.
    /tmp is ephemeral, so durable history should use a database in a future
    production version.
    """
    history = []

    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, OSError, TypeError):
            history = []

    if not isinstance(history, list):
        history = []

    today = datetime.now().date().isoformat()
    history = [entry for entry in history if entry.get("date") != today]
    history.append({"date": today, "stats": stats})
    history = history[-90:]

    # Ensure the writable parent exists when using a custom path.
    parent = os.path.dirname(filepath)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def load_history(filepath: str = DEFAULT_DATA_FILE) -> list[dict]:
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            history = json.load(f)
            return history if isinstance(history, list) else []
    except (json.JSONDecodeError, OSError, TypeError):
        return []


def calculate_progress(history: list[dict]) -> dict:
    if len(history) < 2:
        return {
            "new_easy": 0,
            "new_medium": 0,
            "new_hard": 0,
            "new_total": 0,
        }

    latest = history[-1]["stats"]["solved"]
    previous = history[-2]["stats"]["solved"]

    return {
        "new_easy": latest["easy"] - previous["easy"],
        "new_medium": latest["medium"] - previous["medium"],
        "new_hard": latest["hard"] - previous["hard"],
        "new_total": latest["total"] - previous["total"],
    }
