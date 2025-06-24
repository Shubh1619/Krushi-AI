import google.generativeai as genai
from app.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def generate_ai_answer(question, crop, category, language):
    prompt = f"""
    तुम्ही एक कृषी तज्ञ आहात. एका शेतकऱ्याने विचारले आहे:

    प्रश्न: {question}
    पीक: {crop}
    प्रकार: {category}

    कृपया उत्तर देताना याचे लक्षात घ्या:
    - सल्ला तज्ञाच्या नजरेतून द्या
    - मराठीत सोप्या भाषेत उत्तर द्या
    """
    res = model.generate_content(prompt)
    return res.text

def save_question_to_db(question, crop, language, user_id, state, district, ai_reply):
    # Dummy implementation: return an object with an inserted_id attribute
    class DummyResult:
        def __init__(self):
            self.inserted_id = 1
    return DummyResult()
