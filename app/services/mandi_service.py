import requests
from geopy.distance import geodesic

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

def get_best_market(crop, lat, lon):
    markets = get_all_markets_with_crop(crop)
    markets = [
        {
            **m,
            "pincode": requests.get(
                'https://nominatim.openstreetmap.org/reverse',
                params={"lat": m["lat"], "lon": m["lon"], "format": "json"},
                headers={"User-Agent": "mandi-app"}
            ).json().get("address", {}).get("postcode", ""),
            "distance": round(geodesic((lat, lon), (m["lat"], m["lon"])).km, 2)
        }
        for m in markets
    ]
    sorted_by_price = sorted(markets, key=lambda m: m["avg_price"], reverse=True)
    best = sorted_by_price[0]
    return {
        "पीक": translate_to_marathi(crop),
        "शिफारस केलेला बाजार": translate_to_marathi(best["name"]),
        "किंमत": translate_to_marathi(best["avg_price"]),
        "अंतर (कि.मी.)": translate_to_marathi(best["distance"]),
        "पिनकोड": translate_to_marathi(best.get("pincode", ""))
    }

# Dummy implementation for get_all_markets_with_crop for now
def get_all_markets_with_crop(crop):
    # This should be replaced with actual data fetching logic
    return [
        {"name": "Market A", "lat": 19.1, "lon": 72.9, "avg_price": 2500},
        {"name": "Market B", "lat": 18.5, "lon": 73.8, "avg_price": 2700},
        {"name": "Market C", "lat": 20.0, "lon": 74.5, "avg_price": 2400},
    ]

def get_latest_prices(crop, state=None):
    result = {
        "पीक": translate_to_marathi(crop),
        "राज्य": translate_to_marathi(state) if state else "",
        "नवीनतम किंमत": translate_to_marathi(2600),
        "बाजार": translate_to_marathi("Market B")
    }
    return result

def get_price_history(crop, district, days=15):
    history = [
        {"दिनांक": translate_to_marathi(f"2025-06-{i+1:02d}"), "किंमत": translate_to_marathi(2500 + i*10)} for i in range(days)
    ]
    return {
        "पीक": translate_to_marathi(crop),
        "जिल्हा": translate_to_marathi(district),
        "दिवस": translate_to_marathi(days),
        "इतिहास": history
    }
