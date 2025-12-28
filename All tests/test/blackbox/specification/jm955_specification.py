import storage
from asset import Asset
from asset_manager import AssetManager

def specification_make_manager(monkeypatch):
    monkeypatch.setattr(storage, "save_assets", lambda assets: None)
    monkeypatch.setattr(storage, "load_assets", lambda: [
        Asset("1", "Laptop", "property", 1000, "available")
    ])
    return AssetManager()

#US19
def test_specification_us19_success(monkeypatch):
    manger = specification_make_manager(monkeypatch)
    assert manger.change_asset_status("1", "assigned") == "Status updated successfully"
    assert manger.assets["1"].status == "assigned"

def test_specification_us19_invalid_status(monkeypatch):
    manger = specification_make_manager(monkeypatch)
    assert manger.change_asset_status("1", "broken") == "Valid status is required"

def test_specification_us19_not_found(monkeypatch):
    manager = specification_make_manager(monkeypatch)
    assert manager.change_asset_status("999", "assigned") == "Asset not found"

#US20
def test_specification_us20_end_to_end_reason_attached(monkeypatch):
    manager = specification_make_manager(monkeypatch)
    manager.change_asset_status("1", "assigned")
    assert manager.record_reason_for_change("1", "Loan") == "Reason recorded successfully"
    assert manager.assets["1"].history[-1]["reason"] == "Loan"

#US21
def test_specification_us21_returns_history_after_change(monkeypatch):
    manager = specification_make_manager(monkeypatch)
    manager.change_asset_status("1", "assigned")
    manager.record_reason_for_change("1", "Loan")
    hist = manager.view_status_history("1")
    assert isinstance(hist, list)
    assert hist[-1]["to"] == "assigned"
    assert hist[-1]["reason"] == "Loan"