#All test cases for whitebox loop testing

from asset_manager import AssetManager
from asset import Asset
import storage

def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()


#US28 - Create Inventory Summary
def test_us28_create_inventory_summary_accumulates_over_loop(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [
        Asset("1", "Desk", "property", 100, "available"),
        Asset("2", "Desk2", "property", 100, "available"),
        Asset("3", "Desk3", "property", 100, "available")
    ]

    summary = manager.create_inventory_summary(assets)

    assert summary["property"]["available"]["count"] == 3
    assert summary["property"]["available"]["total_value"] == 300


def test_us28_create_inventory_summary_multiple_categories_and_statuses(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [
        Asset("1", "Desk", "property", 200, "available"),
        Asset("2", "Car", "vehicle", 10000, "assigned"),
        Asset("3", "Phone", "other", 50, "available"),
        Asset("4", "Bike", "vehicle", 300, "available")
    ]

    summary = manager.create_inventory_summary(assets)

    assert summary["property"]["available"]["count"] == 1
    assert summary["vehicle"]["assigned"]["count"] == 1
    assert summary["vehicle"]["available"]["count"] == 1
    assert summary["other"]["available"]["count"] == 1


#US29 - View assets per user
def test_us29_get_assets_per_user_process_all_assets(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [
        Asset("1", "Desk", "property", 200, "assigned", assigned_to="Alice"),
        Asset("2", "Chair", "property", 80, "assigned", assigned_to="Alice"),
        Asset("3", "Car", "vehicle", 10000, "assigned", assigned_to="Bob")
    ]

    result = manager.get_assets_per_user(assets)

    #all 3 assets are processed
    assert len(result) == 3

    #check asset ids appear only once
    asset_ids = [r["asset_id"] for r in result]
    assert asset_ids == ["1", "2", "3"]


#US30 - Depreciation comparison report
def test_us30_create_depreciation_comparison_process_all_assets(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [
        Asset("1", "Desk", "property", 200, "assigned", history=[500]),
        Asset("2", "Chair", "property", 80, "assigned", history=[100]),
        Asset("3", "Car", "vehicle", 10000, "assigned", history=[12000])
    ]

    result = manager.create_depreciation_comparison(assets)

    #all 3 assets are processed
    assert len(result) == 3

    #check asset ids appear only once
    asset_ids = [r["asset_id"] for r in result]
    assert asset_ids == ["1", "2", "3"]

