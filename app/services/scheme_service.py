# Dummy implementations for scheme_service.py

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

def get_gemini_schemes(user_state, user_district, user_crop, user_land_size, user_soil_type, user_category, user_needs):
    """
    Use Gemini to recommend relevant government schemes for a farmer based on input.
    Returns Gemini's response as text (can be parsed as JSON if needed).
    """
    prompt = f"""
Act as an expert agricultural advisor.

I am a farmer in {user_state}, growing {user_crop} on {user_land_size} acres of {user_soil_type} soil. 
I belong to the {user_category} category and I am looking for government schemes 
or subsidies that apply to my situation in {user_district}, {user_state}.

My needs include: {user_needs}.

List only the relevant central and state-level schemes that apply to me. 
For each scheme, include:
- Name
- Type (e.g., subsidy, insurance, loan)
- Description
- Eligibility
- How to apply
- Application link or portal name (if available)

Respond in clean bullet points or JSON format.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ त्रुटी: {str(e)}"
