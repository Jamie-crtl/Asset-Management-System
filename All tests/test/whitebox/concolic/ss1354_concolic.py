from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()



def test_us01_path_missing_id(monkeypatch):
    m = make_manager(monkeypatch, [])
    res = m.create_new_asset({
        "asset_id": "",
        "name": "X",
        "category": "property",
        "value": 1,
        "status": "available",
        "assigned_to": None,
        "history": []
    })
    assert res == "error: missing asset_id"


def test_us01_path_success(monkeypatch):
    m = make_manager(monkeypatch, [])
    res = m.create_new_asset({
        "asset_id": "A1",
        "name": "X",
        "category": "property",
        "value": 1,
        "status": "available",
        "assigned_to": None,
        "history": []
    })
    assert isinstance(res, Asset)
