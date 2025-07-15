# Dummy implementations for scheme_service.py

import json
import re
from app.config import GEMINI_API_KEY
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_all_schemes(state=None, crop=None):
    # Return a list of dummy schemes
    return [
        {"id": "1", "name": "PM Kisan", "state": state or "All", "crops": [crop or "all"]},
        {"id": "2", "name": "Fasal Bima Yojana", "state": state or "All", "crops": [crop or "all"]}
    ]

def get_scheme_by_id(scheme_id):
    # Return a dummy scheme by id
    return {"id": scheme_id, "name": "PM Kisan", "state": "All", "crops": ["all"]}

def get_recommended_schemes(user_id):
    # Return a list of dummy recommended schemes
    return [
        {"id": "1", "name": "PM Kisan", "recommended": True},
        {"id": "2", "name": "Fasal Bima Yojana", "recommended": True}
    ]

def get_gemini_schemes(state, district, crop, land, soil, category, needs):
    prompt = f"""
    You are an expert agricultural advisor.

    I am a farmer in {state}, growing {crop} on {land} acres of {soil} soil. 
    I belong to the {category} category and live in {district}, {state}.
    I need help with: {needs}.

    🔁 List only the central and Maharashtra government schemes I’m eligible for.
    ✅ Respond in **clean JSON array** (without markdown or explanation) in Marathi language (lang: mr) with keys:
    - name
    - type
    - description
    - eligibility
    - how_to_apply
    - application_portal
    
    Output must be in Marathi (lang: mr) only.
    """
    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        # Extract JSON inside the markdown ```json ... ``` block
        match = re.search(r"```json\s*(.*?)\s*```", raw_text, re.DOTALL)
        if match:
            try:
                schemes_list = json.loads(match.group(1))
                return {"schemes": schemes_list}
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON from Gemini output"}
        else:
            # Try to parse the whole response as JSON if no markdown block
            try:
                schemes_list = json.loads(raw_text)
                return {"schemes": schemes_list}
            except json.JSONDecodeError:
                return {"error": "No valid JSON found in Gemini output"}
    except Exception as e:
        return {"error": str(e)}
