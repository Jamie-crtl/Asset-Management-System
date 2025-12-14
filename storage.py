import json
from asset import Asset

DATA_FILE = "assets.json"

def save_assets(assets):
    data = []
    for a in assets:
        data.append({
            "id": a.id,
            "name": a.name,
            "category": a.category,
            "value": a.value,
            "status": a.status,
            "assigned_to": a.assigned_to,
            "history": a.history
        })
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_assets():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        assets = []
        for d in data:
            assets.append(Asset(
                d["id"], d["name"], d["category"],
                d["value"], d["status"],
                d.get("assigned_to"),
                d.get("history", [])
            ))
        return assets

    except FileNotFoundError:
        return []