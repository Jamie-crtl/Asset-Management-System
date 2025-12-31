import storage
from asset import Asset
from asset_manager import AssetManager

def symbolic_make_manager(monkeypatch):
    monkeypatch.setattr(storage, "save_assets", lambda assets: None)
    monkeypatch.setattr(storage, "load_assets", lambda: [
        Asset("1", "Laptop", "property", 1000, "available")
    ])

    return AssetManager()

#US19: change asset status - symbolic whitebox technique
def test_symbolic_us19_asset_id_none(monkeypatch):
    manager = symbolic_make_manager(monkeypatch)
    assert manager.change_asset_status(None, "assigned") == "Valid asset_id is required"

def test_symbolic_us19_asset_not_found(monkeypatch):
    manager = symbolic_make_manager(monkeypatch)
    assert manager.change_asset_status("999", "assigned") == "Asset not found"

def test_symbolic_us19_success(monkeypatch):
    manager = symbolic_make_manager(monkeypatch)
    assert manager.change_asset_status("1", "assigned") == "Status updated successfully"
