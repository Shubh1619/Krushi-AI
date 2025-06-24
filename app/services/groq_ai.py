from app.config import GEMINI_API_KEY
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def diagnose_crop_from_image(file_bytes: bytes, crop: str) -> str:
    try:
        prompt = f"""
        तुम्ही एक अनुभवी कृषी डॉक्टर आहात. खालील माहिती मराठीत आणि मुद्देसूद स्वरूपात द्या:
        1. पिकाचे नाव: {crop}
        2. रोगाचे नाव
        3. रोग का होतो?
        4. उपाय/उपचार
        5. अतिरिक्त सूचना किंवा टीप
        कृपया उत्तर व्यावसायिक कृषी तज्ज्ञासारखे द्या, बोटसारखे नाही.
        खालील पानाच्या प्रतिमेवरून वरील माहिती द्या:
        """
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": file_bytes}
        ])
        return response.text
    except Exception as e:
        return f"❌ त्रुटी: {str(e)}"
