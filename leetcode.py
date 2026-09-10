import requests
import json
import os
from datetime import datetime

LEETCODE_API = "https://leetcode.com/graphql"

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
        response = requests.post(LEETCODE_API, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        user = data.get("data", {}).get("matchedUser")
        if not user:
            return None

        submissions = user["submitStatsGlobal"]["acSubmissionNum"]
        counts = {item["difficulty"]: item["count"] for item in submissions}

        calendar = user.get("userCalendar", {})
        streak = calendar.get("streak", 0)
        total_active_days = calendar.get("totalActiveDays", 0)

        raw_calendar = calendar.get("submissionCalendar", "{}")
        submission_map = json.loads(raw_calendar)
        recent_days = get_recent_activity(submission_map, days=7)

        return {
            "username": user["username"],
            "real_name": user["profile"].get("realName", ""),
            "ranking": user["profile"].get("ranking", 0),
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
    except requests.exceptions.RequestException:
        return None


def get_recent_activity(submission_map: dict, days: int = 7) -> list[dict]:
    from datetime import timezone, timedelta
    today = datetime.now(timezone.utc).date()
    activity = []
    for i in range(days):
        day = today - timedelta(days=i)
        timestamp = str(int(datetime(day.year, day.month, day.day,
                                     tzinfo=timezone.utc).timestamp()))
        count = submission_map.get(timestamp, 0)
        activity.append({"date": day.isoformat(), "submissions": count})
    return list(reversed(activity))


def save_daily_snapshot(stats: dict, filepath: str = "data.json"):
    history = []
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    today = datetime.now().date().isoformat()
    history = [entry for entry in history if entry.get("date") != today]
    history.append({"date": today, "stats": stats})
    history = history[-90:]

    with open(filepath, "w") as f:
        json.dump(history, f, indent=2)


def load_history(filepath: str = "data.json") -> list[dict]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def calculate_progress(history: list[dict]) -> dict:
    if len(history) < 2:
        return {"new_easy": 0, "new_medium": 0, "new_hard": 0, "new_total": 0}
    latest   = history[-1]["stats"]["solved"]
    previous = history[-2]["stats"]["solved"]
    return {
        "new_easy":   latest["easy"]   - previous["easy"],
        "new_medium": latest["medium"] - previous["medium"],
        "new_hard":   latest["hard"]   - previous["hard"],
        "new_total":  latest["total"]  - previous["total"],
    }
