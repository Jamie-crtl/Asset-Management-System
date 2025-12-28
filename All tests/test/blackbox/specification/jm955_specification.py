import storage
from asset import Asset
from asset_manager import AssetManager

def specification_make_manager(monkeypatch):
    monkeypatch.setattr(storage, "save_assets", lambda assets: None)
    monkeypatch.setattr(storage, "load_assets", lambda: [
        Asset("A1", "Laptop", "property", 1000, "available")
    ])
    return AssetManager()

#US19
def test_specification_us19_success(monkeypatch):
    manger = specification_make_manager(monkeypatch)
    assert manger.change_asset_status("A1", "assigned") == "Status updated successfully"
    assert manger.assets["A1"].status == "assigned"

def test_specification_us19_invalid_status(monkeypatch):
    manger = specification_make_manager(monkeypatch)
    assert manger.change_asset_status("A1", "broken") == "Valid status is required"

def test_specification_us19_not_found(monkeypatch):
    manager = specification_make_manager(monkeypatch)
    assert manager.change_asset_status("A999", "assigned") == "Asset not found"