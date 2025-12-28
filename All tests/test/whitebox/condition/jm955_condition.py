import storage
from asset import Asset
from asset_manager import AssetManager

def condition_make_manager(monkeypatch):
    monkeypatch.setattr(storage, "save_assets", lambda assets: None)
    monkeypatch.setattr(storage, "load_assets", lambda: [
        Asset("A1", "Laptop", "property", 1000, "available")
    ])
    return AssetManager()

#US19
def test_condition_us19_asset_id_none(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    assert manager.change_asset_status(None, "assigned") == "Valid asset_id is required"

def test_condition_us19_same_status(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    assert manager.change_asset_status("A1", "available") == "Status already set"
