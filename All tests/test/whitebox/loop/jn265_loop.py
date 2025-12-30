from asset_manager import AssetManager
from asset import Asset
import storage

def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()


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
