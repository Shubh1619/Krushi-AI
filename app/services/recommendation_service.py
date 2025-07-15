from app.config import GEMINI_API_KEY
import google.generativeai as genai
import json
from deep_translator import GoogleTranslator  # Marathi translation

# Gemini API configuration
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def recommend_fertilizer_marathi(crop: str, soil_type: str, stage: str) -> dict:
    """
    Gemini API वापरून खताच्या मराठी शिफारसी परत करणारा फंक्शन.
    """
    prompt = f"""
You are an agricultural expert system. Provide fertilizer recommendations and general advice for the given crop, soil type, and crop stage.

Respond ONLY in valid JSON format. Do not include any explanation or text outside the JSON.

JSON Structure Requirement:
{{
    "recommendations": [
        {{
            "fertilizer": "Name of fertilizer (e.g., DAP, Urea, MOP, Zinc Sulfate)",
            "quantity_per_acre_kg": "Recommended quantity in kg per acre (use ranges where appropriate, e.g., '20-25')",
            "application_tip": "Specific advice for applying this fertilizer for {crop} at the {stage} stage in {soil_type} soil, including method (e.g., basal application, incorporate into soil), and its primary benefit for this specific crop and stage."
        }}
    ],
    "general_notes": "A concise summary of crucial broader advice for {crop} at {stage} in {soil_type} soil, like the importance of soil testing, incorporating organic matter, and the need for split applications if applicable."
}}

Input Details:
Crop: {crop}
Soil Type: {soil_type}
Crop Stage: {stage}

Important Directive: Tailor all recommendations and tips *specifically* for the provided Crop, Soil Type, and Crop Stage. Do not use generic advice unless it is universally applicable and relevant.
    """
    try:
        response = model.generate_content(prompt)
        raw_text = response.text

        # Remove Markdown fences
        if raw_text.startswith("```json"):
            raw_text = raw_text[len("```json"):].strip()
        if raw_text.endswith("```"):
            raw_text = raw_text[:-len("```")].strip()

        parsed_json = json.loads(raw_text)

        # Translate the JSON content to Marathi
        translated = {
            "recommendations": [],
            "general_notes": GoogleTranslator(source='en', target='mr').translate(parsed_json["general_notes"])
        }

        for item in parsed_json["recommendations"]:
            translated_item = {
                "fertilizer": GoogleTranslator(source='en', target='mr').translate(item["fertilizer"]),
                "quantity_per_acre_kg": item["quantity_per_acre_kg"],
                "application_tip": GoogleTranslator(source='en', target='mr').translate(item["application_tip"])
            }
            translated["recommendations"].append(translated_item)

        return translated

    except json.JSONDecodeError as e:
        return {"error": f"JSON parsing अयशस्वी: {e}", "raw_response": raw_text}
    except Exception as e:
        return {"error": str(e)}

