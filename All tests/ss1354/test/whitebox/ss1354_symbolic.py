from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()


def test_us02_symbolic_get_returns_same_object(monkeypatch): #
    a = Asset("A1", "Laptop", "other", 100, "available", None, [])
    m = make_manager(monkeypatch, [a])
    got = m.get_asset_by_id("A1")
    assert got is not None
    assert got.id == "A1"

def test_us03_symbolic_all_ids_appear(monkeypatch):#
    assets = [
        Asset("A1", "Laptop", "other", 100, "available", None, []),
        Asset("B2", "Desk", "other", 200, "available", None, []),
    ]
    m = make_manager(monkeypatch, assets)
    out = m.list_assets()

    assert all(f"{a.id}:" in out for a in assets)