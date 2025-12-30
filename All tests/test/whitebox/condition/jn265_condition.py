from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()


def test_us28_create_inventory_summary_not_list(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assert manager.create_inventory_summary("test: not a list") == "Assets must be provided in a list"


def test_us28_create_inventory_summary_asset_is_none(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assert manager.create_inventory_summary([None]) == "Asset not found"


def test_us28_create_inventory_summary_negative_asset_value(monkeypatch):
    manager = make_manager(monkeypatch, [])
    asset = Asset("1", "Desk", "property", 10, "available")
    #bypasses Asset validation
    asset.value = -1
    assert manager.create_inventory_summary([asset]) == "Asset is missing value or has negative value"

