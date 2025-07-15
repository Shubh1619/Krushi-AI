import requests

def get_pincode_from_latlon(lat: float, lon: float):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    try:
        response = requests.get(url, timeout=5, headers={"User-Agent": "weather-app"})
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            pincode = address.get("postcode")
            city = address.get("city") or address.get("town") or address.get("village")
            state = address.get("state")
            return {
                "pincode": pincode,
                "city": city,
                "state": state,
                "full_address": address
            }
        else:
            return {"error": "Location not found."}
    except Exception:
        return {"error": "Unable to fetch location details."}

def get_full_weather(city: str):
    url = f"https://wttr.in/{city}?format=j1"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()  # Return all weather data
        else:
            return {"error": "City not found! Please enter a valid city name."}
    except Exception:
        return {"error": "Unable to fetch weather data. Please try again later."}

def translate_to_marathi(text: str) -> str:
    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=mr&dt=t&q=" + requests.utils.quote(text)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # The response is a nested list, extract the translation
            result = response.json()
            return ''.join([item[0] for item in result[0]])
        else:
            return text
    except Exception:
        return text

def get_current_weather(city: str):
    data = get_full_weather(city)
    if "error" in data:
        return {"त्रुटी": translate_to_marathi(data["error"])}
    try:
        current = data["current_condition"][0]
        return {
            "शहर": translate_to_marathi(city),
            "तापमान (°C)": translate_to_marathi(current["temp_C"]),
            "आर्द्रता": translate_to_marathi(current["humidity"]),
            "वर्णन": translate_to_marathi(current["weatherDesc"][0]["value"])
        }
    except Exception:
        return {"त्रुटी": translate_to_marathi("Unable to parse current weather data.")}

def get_crop_advisory(crop: str, stage: str, city: str):
    weather = get_current_weather(city)
    if "त्रुटी" in weather:
        return {
            "पीक": translate_to_marathi(crop),
            "टप्पा": translate_to_marathi(stage),
            "सल्ला": [weather["त्रुटी"]]
        }
    try:
        temp = float(weather["तापमान (°C)"])
        advice = []
        if stage.lower() == "sowing":
            if temp < 20:
                advice.append("तापमान कमी आहे. शक्य असल्यास पेरणी पुढे ढकला.")
            else:
                advice.append("पेरणीसाठी योग्य तापमान आहे.")
            if crop.lower() == "cotton":
                advice.append("कापूस पेरणीसाठी आदर्श तापमान २५–३०°C आहे.")
        elif stage.lower() == "flowering" and temp > 38:
            advice.append("उच्च तापमान आढळले. उष्णता तणाव कमी करण्यासाठी मल्चिंग वापरा.")
        elif stage.lower() == "plantation":
            advice.append("लागवडीच्या टप्प्यात मातीतील ओलावा तपासा आणि योग्य सिंचन करा.")
        if not advice:
            advice.append("या टप्प्यासाठी विशिष्ट सल्ला नाही. पीक आणि हवामान स्थिती नियमितपणे तपासा.")
        return {
            "पीक": translate_to_marathi(crop),
            "टप्पा": translate_to_marathi(stage),
            "सल्ला": [translate_to_marathi(a) for a in advice]
        }
    except Exception:
        return {
            "पीक": translate_to_marathi(crop),
            "टप्पा": translate_to_marathi(stage),
            "सल्ला": [translate_to_marathi("Unable to generate advisory due to weather data error.")]
        }
