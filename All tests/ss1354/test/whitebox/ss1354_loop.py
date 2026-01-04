from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()

def test_us03_loop_zero_assets(monkeypatch): # a loop test with 0 iterations, checks cases where the asset dictionary is empty
    m = make_manager(monkeypatch, [])
    assert m.list_assets() == "ERROR: NO ASSETS AVAILABLE"


def test_us03_loop_one_asset(monkeypatch): # a loop test with one iteration, checks if asset a1 is included in the output
    m = make_manager(monkeypatch, [Asset("A1", "residential", "property", 1000900, "available", None, [])])
    out = m.list_assets()
    assert "A1:" in out


def test_us03_loop_many_assets(monkeypatch): # a loop test over more assets, similar to one above but just tests more ids
    m = make_manager(monkeypatch, [
        Asset("A1", "Laptop", "other", 100, "available", None, []),
        Asset("B2", "Desk", "other", 200, "available", None, []),
        Asset("C3", "Phone", "other", 50, "available", None, []),
    ])
    out = m.list_assets()
    assert "A1:" in out and "B2:" in out and "C3:" in out

def test_us06_loop_required_fields_fail_early(monkeypatch): # ensures that validate_required_fields returns false as soon as an empty required field is detected
    m = make_manager(monkeypatch, [])
    assert m.validate_required_fields({
        "name": "",  # fail early
        "category": "property",
        "value": 100,
        "status": "available",
        "assigned_to": None,
        "history": []
    }) is False