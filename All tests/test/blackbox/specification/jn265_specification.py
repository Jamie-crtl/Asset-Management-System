#All test cases for blackbox specification testing

from asset_manager import AssetManager
from asset import Asset
import storage

def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()


#US28 - Create Inventory Summary
def test_us28_create_inventory_summary_by_category_and_status(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [
        Asset("1", "Desk", "property", 200, "available"),
        Asset("2", "Chair", "property", 80, "available"),
        Asset("3", "Car", "vehicle", 10000, "assigned"),
        Asset("4", "Old Phone", "other", 25, "disposed"),
        Asset("5", "Spare Car", "vehicle", 5000, "assigned")
    ]

    summary = manager.create_inventory_summary(assets)

    #
    assert summary["property"]["available"]["count"] == 2
    assert summary["property"]["available"]["total_value"] == 280

    assert summary["vehicle"]["assigned"]["count"] == 2
    assert summary["vehicle"]["assigned"]["total_value"] == 15000

    assert summary["other"]["disposed"]["count"] == 1
    assert summary["other"]["disposed"]["total_value"] == 25

def test_us28_create_inventory_summary_single_asset(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [Asset("1", "Desk", "property", 200, "available")]

    summary = manager.create_inventory_summary(assets)

    #example summary with one asset description
    assert summary == {
        "property": {
            "available": {
                "count": 1,
                "total_value": 200
            }
        }
    }

def test_us28_create_inventory_summary_empty_list(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = []

    summary = manager.create_inventory_summary(assets)

    assert summary == {}


#US29 - View assets per user
def test_us29_get_assets_per_user_returns_list_of_dicts(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [
        Asset("1", "Desk", "property", 200, "assigned", assigned_to="Alice"),
        Asset("2", "Car", "vehicle", 10000, "assigned", assigned_to="Bob")
    ]

    result = manager.get_assets_per_user(assets)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], dict)

    assert result[0]["asset_id"] == "1"
    assert result[0]["name"] == "Desk"
    assert result[0]["category"] == "property"
    assert result[0]["status"] == "assigned"
    assert result[0]["assigned_to"] == "Alice"


def test_us29_get_assets_per_user_unassigned_label(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [
        Asset("1", "Laptop", "other", 900, "available", assigned_to=None),
        Asset("2", "Monitor", "property", 150, "available", assigned_to="")
    ]

    result = manager.get_assets_per_user(assets)

    assigned_values = [r["assigned_to"] for r in result]

    assert assigned_values == ["Unassigned", "Unassigned"]

