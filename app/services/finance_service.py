from pathlib import Path
import json

DATA_FILE = Path("app/models/finance_data.json")

def read_finance_data():
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def write_finance_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def add_finance_record(crop, season, expenses, income):
    # Calculate totals
    total_expense = sum(expenses.values())
    total_income = income["quantity"] * income["rate_per_kg"]
    net_profit = total_income - total_expense

    record = {
        "crop": crop,
        "season": season,
        "expenses": expenses,
        "income": {
            "quantity": income["quantity"],
            "rate_per_kg": income["rate_per_kg"],
            "total": total_income
        },
        "net_profit": net_profit
    }

    data = read_finance_data()
    data.append(record)
    write_finance_data(data)

    return {
        "message": f"{crop} record saved successfully.",
        "net_profit": net_profit,
        "status": "Profit" if net_profit >= 0 else "Loss"
    }

def get_all_finance_records():
    return read_finance_data()

def get_records_by_crop(crop):
    return [r for r in read_finance_data() if r["crop"].lower() == crop.lower()]
