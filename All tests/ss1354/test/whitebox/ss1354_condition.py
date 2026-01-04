from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()


def test_us01_branch_missing_id(monkeypatch):# this is a condition test on the branch where asset_id is missing or empty
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



def test_us01_branch_duplicate(monkeypatch): # this tests the branch where an asset allready exists with the same id
    m = make_manager(monkeypatch, [Asset("A1", "abc", "property", 1, "available", None, [])])
    res = m.create_new_asset({
        "asset_id": "A1",
        "name": "abc",
        "category": "property",
        "value": 1,
        "status": "available",
        "assigned_to": None,
        "history": []
    })
    assert res == "duplicate asset_id"

def test_us04_branch_invalid_field(monkeypatch): # this tests the branch where an invalid field name is given to update a previous asset
    m = make_manager(monkeypatch, [Asset("A1", "Laptop", "other", 1, "available", None, [])])
    assert m.update_asset_field("A1", "invalid", "huhuhuhuhuhuhuhuhuhuhuhuhuh") is False

def test_us05_branch_missing(monkeypatch): # exercises the branch where delete_asset() is called with an invalid id
    m = make_manager(monkeypatch, [])
    assert m.delete_asset("dsuaduashds87ad78ad") is False
