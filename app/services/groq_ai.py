from app.config import GEMINI_API_KEY
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def diagnose_crop_from_image(file_bytes: bytes, crop: str) -> str:
    try:
        prompt = f"""
        तुम्ही एक अत्यंत अनुभवी आणि विश्वासार्ह कृषी डॉक्टर आहात.
        खालील माहिती मराठीत आणि मुद्देसूद स्वरूपात द्या:

        1. पिकाचे नाव: {crop}
        2. रोगाचे नाव
        3. रोग का होतो?
        4. योग्य आणि निश्चित उपाय/उपचार
        5. अतिरिक्त सूचना किंवा टीप

        कृपया खालील प्रतिमेवर आधारित निदान द्या.
        """

        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": file_bytes}
        ])

        result_text = response.text

        # चेक करा की प्रतिमा कृषीसंबंधी आहे की नाही
        non_crop_keywords = ["जहाज", "इमारत", "मनुष्य", "प्राणी", "समुद्र", "वाहन", "शस्त्र"]

        if any(keyword in result_text for keyword in non_crop_keywords):
            return "⚠️ दिलेली प्रतिमा पिकाशी संबंधित नाही. कृपया पानं, फळं किंवा झाडाची प्रतिमा पाठवा."

        # अस्वीकरण वगैरे काढून स्वच्छ टेक्स्ट तयार करा
        ignore_phrases = ["नोंद:", "अस्वीकरण:"]
        for phrase in ignore_phrases:
            if phrase in result_text:
                result_text = result_text.split(phrase)[0].strip()

        return result_text

    except Exception as e:
        return f"❌ त्रुटी: {str(e)}"