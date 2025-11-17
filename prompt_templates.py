# prompt_templates.py

# ANGLE_PROMPT_TEMPLATE requests structured JSON output with exact_count parameter
ANGLE_PROMPT_TEMPLATE = """
You are a creative ad strategist for {brand}. The target audience is {audience}. Ads must be {ad_length} seconds (15-20s ideal) and must hook within 0-3 seconds.
User request: {user_query}

Task:
1) Produce exactly {exact_count} completely novel creative angles for a luxury mattress ad. For each angle, include these fields in a JSON array (no extra text):
[
  {{
    "id": 1,
    "title": "<short title>",
    "hook": "<what happens in seconds 0-3>",
    "description": "<1-sentence concept description>",
    "why": "<Why it will resonate with {audience}>",
    "differentiation": "<How this differs from existing mattress ads>"
  }},
  ...
]

Constraints:
- Output must be valid JSON only (an array of objects). Do NOT include additional commentary outside JSON.
- Each object must have all five fields: id (1..N), title, hook, description, why, differentiation.
- Avoid any mattress-category clichés or overused formats. Aim for premium, cinematic, original ideas.

Return only the JSON array.
"""

SCRIPT_PROMPT_TEMPLATE = """
You are transforming a creative concept for {brand} into {ad_length}-second YouTube ad script(s) for {audience}.
Use this structured concept (pass-through) to build {variation_count} variation(s).

Structured concept:
Title: {title}
Hook: {hook}
Description: {description}
Why: {why}
Differentiation: {differentiation}

Tone: {tone}
Format each variation as:
[00:00–00:03] HOOK — description
[00:03–00:08] Scene 1 — description
[00:08–00:14] Scene 2 — description
[00:14–00:20] Wrap-up + CTA

Also include:
VO:
On-screen text:
Sound:

Keep scripts concise, cinematic, and optimized for immediate hook and high conversion for an affluent audience. Produce output as JSON:
[
  {{
    "variation_id": 1,
    "title": "...",
    "script_timed": "...", 
    "vo": "...",
    "on_screen_text": "...",
    "sound": "...",
    "cta": "..."
  }},
  ...
]
Return only the JSON array(s).
"""
