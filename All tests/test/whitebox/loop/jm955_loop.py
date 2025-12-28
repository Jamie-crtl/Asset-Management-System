import storage
from asset import Asset
from asset_manager import AssetManager


def loop_make_manager_history(monkeypatch, history):
    monkeypatch.setattr(storage, "save_assets", lambda assets: None)
    monkeypatch.setattr(storage, "load_assets", lambda: [
        Asset("1", "Laptop", "property", 1000, "available", history=history)
    ])
    return AssetManager()

#US21
def test_loop_us21_asset_not_found(monkeypatch):
    manager = loop_make_manager_history(monkeypatch, [])
    assert manager.view_status_history("999") == "Asset not found"

def test_loop_us21_zero_history(monkeypatch):
    manager = loop_make_manager_history(monkeypatch, [])
    assert manager.view_status_history("1") == "No status history available"

def test_loop_us21_one_history(monkeypatch):
    manager = loop_make_manager_history(monkeypatch, [
        {"from": "available", "to": "assigned", "reason": "Loan"}
    ])
    hist = manager.view_status_history("1")
    assert isinstance(hist, list)
    assert len(hist) == 1
    assert hist[0]["to"] == "assigned"

def test_loop_many_history(monkeypatch):
    manager = loop_make_manager_history(monkeypatch, [
        {"from": "available", "to": "assigned", "reason": "Loan"},
        {"from": "assigned", "to": "disposed", "reason": "Broken"},
    ])
    hist = manager.view_status_history("1")
    assert isinstance(hist, list)
    assert len(hist) == 2
    assert hist[-1]["to"] == "disposed"
