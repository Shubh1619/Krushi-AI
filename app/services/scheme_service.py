# Dummy implementations for scheme_service.py

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
