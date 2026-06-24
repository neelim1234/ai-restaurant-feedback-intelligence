"""
backend/ai/gemini_client.py - Direct REST API client for Gemini using HTTPX.
"""

import httpx
import json
import logging
from config import settings

logger = logging.getLogger("uvicorn")

def call_gemini(prompt: str) -> str:
    """
    Sends the prompt directly to Gemini REST API via httpx.
    Raises RuntimeError if the key is not set, or if the API call fails/times out.
    """
    api_key = settings.GEMINI_API_KEY.strip()
    
    if not api_key or "PLACEHOLDER" in api_key.upper() or api_key.startswith("<"):
        logger.error("GEMINI_API_KEY is not configured in backend/.env")
        raise RuntimeError("Gemini service unavailable")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("Empty candidates in Gemini response")
                
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if not text:
                raise ValueError("No text generated in candidate response")
                
            return text.strip()

    except Exception as e:
        logger.error(f"Gemini API request failed: {e}")
        raise RuntimeError("Gemini service unavailable")
