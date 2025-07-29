import httpx
import json
import re
from app.config import GEMINI_API_KEY
import google.generativeai as genai
from fastapi import HTTPException

# Configure Gemini model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Common User-Agent header for CoWIN API
COWIN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/119.0.0.0 Safari/537.36"
}

# Dummy scheme list for fallback or testing
def get_all_schemes(state=None, crop=None):
    return [
        {"id": "1", "name": "PM Kisan", "state": state or "All", "crops": [crop or "all"]},
        {"id": "2", "name": "Fasal Bima Yojana", "state": state or "All", "crops": [crop or "all"]}
    ]

# Dummy single scheme by ID
def get_scheme_by_id(scheme_id):
    return {"id": scheme_id, "name": "PM Kisan", "state": "All", "crops": ["all"]}

# Dummy recommended schemes
def get_recommended_schemes(user_id):
    return [
        {"id": "1", "name": "PM Kisan", "recommended": True},
        {"id": "2", "name": "Fasal Bima Yojana", "recommended": True}
    ]

# Gemini-based scheme recommendation
def get_gemini_schemes(state, district, crop, land, soil, category, needs):
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

        # Try extracting JSON from inside ```json block
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

# ✅ Updated: Fetch states from CoWIN API with proper headers
async def get_all_states():
    url = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=COWIN_HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch states")

# ✅ Updated: Fetch districts from CoWIN API with proper headers
async def get_districts_by_state(state_id: int):
    url = f"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=COWIN_HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch districts")
