import storage
from asset import Asset
from asset_manager import AssetManager

def concolic_make_manager(monkeypatch):
    monkeypatch.setattr(storage, "save_assets", lambda assets: None)
    monkeypatch.setattr(storage, "load_assets", lambda: [
        Asset("1", "Laptop", "property", 1000, "available"),
        Asset("2", "Car", "vehicle", 5000, "assigned"),  # used for "same status" path
    ])

    return AssetManager()

#US19: change asset status - concolic whitebox technique

def test_concolic_us19_base_path_success(monkeypatch):
    manager = concolic_make_manager(monkeypatch)
    res = manager.change_asset_status("1", "assigned")
    assert res == "Status updated successfully"

def test_concolic_us19_negate_asset_exists(monkeypatch):
    manager = concolic_make_manager(monkeypatch)
    res = manager.change_asset_status("999", "assigned")
    assert res == "Asset not found"

def test_concolic_us19_negate_status_is_valid(monkeypatch):
    manager = concolic_make_manager(monkeypatch)
    res = manager.change_asset_status("1", "broken")
    assert res == "Valid status is required"

def test_concolic_us19_negate_status_changes(monkeypatch):
    manager = concolic_make_manager(monkeypatch)
    res = manager.change_asset_status("2", "assigned")
    assert res == "Status already set"