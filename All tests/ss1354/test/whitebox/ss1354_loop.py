from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()

def test_us03_loop_zero_assets(monkeypatch):
    m = make_manager(monkeypatch, [])
    assert m.list_assets() == "ERROR: NO ASSETS AVAILABLE"


def test_us03_loop_one_asset(monkeypatch):
    m = make_manager(monkeypatch, [Asset("A1", "Laptop", "property", 100, "available", None, [])])
    out = m.list_assets()
    assert "A1:" in out


def test_us03_loop_many_assets(monkeypatch):
    m = make_manager(monkeypatch, [
        Asset("A1", "Laptop", "property", 100, "available", None, []),
        Asset("B2", "Desk", "property", 200, "available", None, []),
        Asset("C3", "Phone", "other", 50, "available", None, []),
    ])
    out = m.list_assets()
    assert "A1:" in out and "B2:" in out and "C3:" in out

def test_us06_loop_required_fields_fail_early(monkeypatch):
    m = make_manager(monkeypatch, [])
    assert m.validate_required_fields({
        "name": "",  # fail early
        "category": "property",
        "value": 100,
        "status": "available",
        "assigned_to": None,
        "history": []
    }) is False