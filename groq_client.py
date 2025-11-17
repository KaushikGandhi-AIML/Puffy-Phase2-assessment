"""
Thin Groq API wrapper.
Replace with the official Groq SDK if you have it.
Expect environment variables:
  - GROQ_API_URL  (e.g. https://api.groq.ai/v1/...)
  - GROQ_API_KEY

This wrapper posts JSON:
{
  "model": "gpt-like-model-or-id",
  "messages": [{"role":"system","content": "..."},
               {"role":"user","content": "..."}],
  "max_tokens": 512
}
and returns a parsed dict with 'text' key mapping to model output.
"""

import os
import requests
import json
from typing import Optional

DEFAULT_MODEL = "llama-3.3-70b-versatile"  # replace with actual model id

class GroqClient:
    def __init__(self, api_url: Optional[str]=None, api_key: Optional[str]=None, model: Optional[str]=None):
        self.api_url = api_url or os.environ.get("GROQ_API_URL")
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.model = model or DEFAULT_MODEL
        if not self.api_url or not self.api_key:
            # We will not fail hard here so the UI can still load; but calls will error.
            print("Warning: GROQ_API_URL or GROQ_API_KEY not set in env.")

    def create_chat_completion(self, system_prompt: str, user_prompt: str, max_tokens: int=1024, temperature: float=0.8):
        if not self.api_url or not self.api_key:
            return {"error": "GROQ_API_URL or GROQ_API_KEY not configured."}

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            r = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            resp = r.json()
            # try common response shapes
            if isinstance(resp, dict):
                # possible shapes:
                # { "choices": [ { "message": {"content": "..."}} ] }
                if "choices" in resp and len(resp["choices"]) > 0:
                    first = resp["choices"][0]
                    # gpt-style
                    content = first.get("message", {}).get("content") or first.get("text") or first.get("output", "")
                    return {"text": content, "raw": resp}
                # or: { "output": "text..." } or { "text": "..." }
                if "output" in resp:
                    return {"text": resp["output"], "raw": resp}
                if "text" in resp:
                    return {"text": resp["text"], "raw": resp}
            # fall back
            return {"text": json.dumps(resp)}
        except Exception as e:
            return {"error": str(e), "status_code": getattr(e, "response", None) and getattr(e.response, "status_code", None)}

