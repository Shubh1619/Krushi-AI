from pathlib import Path
import json
from datetime import datetime, timedelta

# ✅ Safe pathing (cross-platform)
CROP_FILE = Path("app/models/crops.json")
DATA_FILE = Path("app/models/calendar_data.json")

# ------------------ 🔁 Crop Lifecycle Management ------------------

def read_crops():
    if not CROP_FILE.exists():
        return {}
    try:
        with open(CROP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def write_crops(data):
    CROP_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CROP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_new_crop(crop_name, lifecycle):
    crops = read_crops()
    crops[crop_name.lower()] = lifecycle
    write_crops(crops)
    return {"message": f"Crop '{crop_name}' added with lifecycle."}

def get_crop_lifecycle(crop_name):
    crops = read_crops()
    return crops.get(crop_name.lower())

# ------------------ 🧾 Calendar Data Storage ------------------

def read_calendar():
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def write_calendar(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ------------------ 📅 Calendar Generation ------------------

def generate_calendar(crop, sowing_date, lifecycle):
    # Try both 'YYYY-MM-DD' and 'DD-MM-YYYY' formats
    sowing = None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            sowing = datetime.strptime(sowing_date, fmt)
            break
        except ValueError:
            continue
    if sowing is None:
        raise ValueError(f"Invalid date format: {sowing_date}. Use YYYY-MM-DD or DD-MM-YYYY.")
    calendar = []
    for step in lifecycle:
        event_date = sowing + timedelta(days=step["day"])
        calendar.append({
            "crop": crop,
            "date": event_date.strftime("%Y-%m-%d"),
            "task": step["task"],
            "tip": step["tip"]
        })
    return calendar

def save_calendar(crop, sowing_date, lifecycle):
    data = read_calendar()
    new_items = generate_calendar(crop, sowing_date, lifecycle)
    data.extend(new_items)
    write_calendar(data)
    return new_items

# ------------------ ❌ Task Deletion ------------------

def delete_task_by_date(task_date, task_name):
    data = read_calendar()
    filtered = [t for t in data if not (t["date"] == task_date and t["task"] == task_name)]
    write_calendar(filtered)
    return {"message": f"Task '{task_name}' on {task_date} deleted."}

# (Optional) delete all tasks on a date
def delete_all_tasks_on_date(task_date):
    data = read_calendar()
    filtered = [t for t in data if t["date"] != task_date]
    write_calendar(filtered)
    return {"message": f"All tasks on {task_date} deleted."}
