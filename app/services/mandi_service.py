import requests

# 🌐 Translate English text to Marathi
def translate_to_marathi(text: str) -> str:
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=mr&dt=t&q=" + requests.utils.quote(str(text))
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            return ''.join([item[0] for item in result[0]])
        else:
            return str(text)
    except Exception:
        return str(text)

# 📈 Latest price summary (without showing market name)
def get_latest_prices(crop: str, state: str = None) -> dict:
    return {
        "पीक": translate_to_marathi(crop),
        "राज्य": translate_to_marathi(state if state else ""),
        "नवीनतम किंमत": translate_to_marathi(2600)
    }

# 📊 Simulated crop price history by district
def get_price_history(crop: str, district: str, days: int = 15) -> dict:
    history = [
        {
            "दिनांक": translate_to_marathi(f"2025-06-{i+1:02d}"),
            "किंमत": translate_to_marathi(2500 + i * 10)
        }
        for i in range(days)
    ]
    return {
        "पीक": translate_to_marathi(crop),
        "जिल्हा": translate_to_marathi(district),
        "दिवस": translate_to_marathi(days),
        "इतिहास": history
    }