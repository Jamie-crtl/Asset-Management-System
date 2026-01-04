from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list): # used so that we can do unit tests without affecting real json files
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()



def test_us01_path_missing_id(monkeypatch): # checks the branch where assetId is missing/empty, should return an error
    m = make_manager(monkeypatch, [])
    res = m.create_new_asset({
        "asset_id": "",
        "name": "residential",
        "category": "property",
        "value": 10000000,
        "status": "available",
        "assigned_to": None,
        "history": []
    })
    assert res == "error: missing asset_id"


def test_us01_path_success(monkeypatch):# checks/exercises the path where all fields are valid, and a successful asset instance is created
    m = make_manager(monkeypatch, [])
    res = m.create_new_asset({
        "asset_id": "A1",
        "name": "residential",
        "category": "property",
        "value": 100000000,
        "status": "available",
        "assigned_to": None,
        "history": []
    })
    assert isinstance(res, Asset)

def test_us04_path_invalid_field(monkeypatch):# we have an existing asset in memory but try to update an invalid field that doesnt exist in the asset ( invalid field path)
    m = make_manager(monkeypatch, [Asset("A1", "Laptop", "other", 10, "available", None, [])])
    assert m.update_asset_field("A1", "bad", 123) is False

def test_us05_path_delete_missing(monkeypatch):# we start with no assets and try deleting an asset that doesnt exist ( missing field path)
    m = make_manager(monkeypatch, [])
    assert m.delete_asset("isdha87dgs7a8dg") is False