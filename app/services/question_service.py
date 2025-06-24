import google.generativeai as genai
from app.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


def generate_ai_answer(question, state):
    prompt = f"""
    तुम्ही एक कृषी तज्ञ आहात. एका शेतकऱ्याने विचारले आहे:

    प्रश्न: {question}

    राज्य: {state}

    कृपया उत्तर देताना याचे लक्षात घ्या:
    - राज्याच्या हवामान व शेती स्थितीचा विचार करा
    - सल्ला तज्ञाच्या नजरेतून द्या
    - मराठीत सोप्या भाषेत उत्तर द्या
    - एक समाधानकारक, उपयोगी उत्तर द्या
    """
    res = model.generate_content(prompt)
    return res.text


def save_question_to_db(question, state, ai_reply):
    # Dummy DB save logic (replace with actual MongoDB/SQL code)
    class DummyResult:
        def __init__(self):
            self.inserted_id = 1  # hardcoded for now
    return DummyResult()
