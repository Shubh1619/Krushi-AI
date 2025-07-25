import httpx

import json
import re
from app.config import GEMINI_API_KEY
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_all_schemes(state=None, crop=None):
    """
    Returns a list of dummy schemes for testing.
    """
    return [
        {"id": "1", "name": "PM Kisan", "state": state or "All", "crops": [crop or "all"]},
        {"id": "2", "name": "Fasal Bima Yojana", "state": state or "All", "crops": [crop or "all"]}
    ]

def get_scheme_by_id(scheme_id):
    """
    Returns a dummy scheme by scheme ID.
    """
    return {"id": scheme_id, "name": "PM Kisan", "state": "All", "crops": ["all"]}

def get_recommended_schemes(user_id):
    """
    Returns a list of dummy recommended schemes for the user.
    """
    return [
        {"id": "1", "name": "PM Kisan", "recommended": True},
        {"id": "2", "name": "Fasal Bima Yojana", "recommended": True}
    ]

def get_gemini_schemes(state, district, crop, land, soil, category, needs):
    """
    Uses Gemini to recommend government schemes in Marathi based on user profile.
    """
    prompt = f"""
You are an expert agricultural advisor.

I am a farmer in {state}, growing {crop} on {land} acres of {soil} soil.
I belong to the {category} category and live in {district}, {state}.
I need help with: {needs}.

🔁 List only the central and Maharashtra government schemes I’m eligible for.
✅ Respond in clean JSON array (no markdown or explanation) in Marathi with keys:
- name
- type
- description
- eligibility
- how_to_apply
- application_portal

Response language: Marathi (lang: mr) only.
"""

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Attempt to extract JSON from code block
        match = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL)
        if match:
            raw_json = match.group(1).strip()
        else:
            raw_json = raw_text

        schemes_list = json.loads(raw_json)
        return {"schemes": schemes_list}

    except json.JSONDecodeError:
        return {"error": "Gemini response is not valid JSON"}
    except Exception as e:
        return {"error": str(e)}
    
async def get_all_states():
    url = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

async def get_districts_by_state(state_id: int):
    url = f"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()