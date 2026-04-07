import json
import re
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_json(text):
    match = re.search(r"\[.*\]", text, re.DOTALL)
    return match.group(0) if match else "[]"


def generate_subtasks(task_title, priority_hint):
    prompt = f"""
You are a senior software engineer.

Break this task into subtasks.

Task: {task_title}
Priority strategy: {priority_hint}

Rules:
- Max 8 subtasks
- Each should be clear and actionable
- Adjust based on priority:
    - Fast → fewer, high-impact tasks
    - Precise → more detailed steps

Return ONLY JSON array:
[
  {{ "title": "..." }},
  {{ "title": "..." }}
]
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )

    raw = response.choices[0].message.content

    # 🔥 Clean JSON
    clean = extract_json(raw)

    try:
        data = json.loads(clean)
    except:
        return []

    # ✅ Validate
    valid_subtasks = []

    for item in data:
        if isinstance(item, dict) and "title" in item:
            valid_subtasks.append({
                "title": item["title"]
            })

    return valid_subtasks