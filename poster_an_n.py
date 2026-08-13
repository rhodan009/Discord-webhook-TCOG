#!/usr/bin/env python3
"""
The City of Gold - automatic weekly posting of Year N.

Works out the current golden year (Year 0 = Monday 13 October 2025, +1 per
real Monday) and posts the weekly embed to #golden-calendar via webhook.

LOCAL USE (testing)
  export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
  python3 post_year_n.py

Designed to run every Monday via GitHub Actions (see the accompanying
workflow .github/workflows/year-n.yml) - but works identically as a local
cron job or scheduled task.
"""

import os
import random
import urllib.request
import json
from datetime import date

# ------------------------------------------------------------------ settings

EPOCH = date(2025, 10, 13)          # Monday - Year 0, Day 0
GOLD = 13214247                     # #C9A227

PROMPTS = [
    "Your House has a motto. What is it?",
    "An institution's constitution cannot be rewritten. Which clause would you never risk getting wrong?",
    "A hundred signatures found a religion. One believer keeps it alive. Which would be harder to hold on to?",
    "No county can stand on its own. Would you rather sit on the trade route, or on the mine?",
    "Only a court can end a character for good. Would you accept being a judge?",
    "You pay to school a child who is not yet yours to play. What do you teach them first?",
    "Ten citizens found a hamlet. Who are the nine others you would pick?",
    "A title with no recognition is worth little more than a statement. What earns recognition?",
    "Succession can be planned, or left to chance. Which do you trust less?",
    "Marshals investigate, judges decide. Which office would you rather never hold?",
    "Elections run forty-eight hours. Long enough, or an invitation to campaign?",
    "Your character has eighty weeks. What must be finished before the fiftieth?",
]

# --------------------------------------------------------------------- logic


def golden_year(today: date) -> int:
    """Number of complete real weeks elapsed since the epoch Monday."""
    return (today - EPOCH).days // 7


def weekly_prompt(n: int) -> str:
    """Pick a prompt. Seeded on the year, so a rerun the same Monday
    produces exactly the same message rather than a second, different one."""
    rng = random.Random(n)
    return rng.choice(PROMPTS)


def build_payload(n: int, prompt: str) -> dict:
    return {
        "content": None,
        "embeds": [
            {
                "title": f"\u269c\ufe0f  Year {n} of the Golden Calendar",
                "description": (
                    "A new year opens over Arkadia.\n\n"
                    f"*{prompt}*"
                ),
                "color": GOLD,
            }
        ],
    }


def send(webhook_url: str, payload: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "TCOG-GoldenCalendar (https://thecityofgold.net, 1.0)",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        if response.status not in (200, 204):
            raise RuntimeError(f"Discord returned status {response.status}")


def main() -> None:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise SystemExit("DISCORD_WEBHOOK_URL is not set.")

    today = date.today()
    n = golden_year(today)
    prompt = weekly_prompt(n)
    payload = build_payload(n, prompt)

    print(f"Real date : {today.isoformat()}")
    print(f"Year {n} of the Golden Calendar")
    print(f"Prompt    : {prompt}")

    send(webhook_url, payload)
    print("Message sent.")


if __name__ == "__main__":
    main()
