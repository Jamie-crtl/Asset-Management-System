import pytest
from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    # Stop reading real assets.json during tests
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    return AssetManager()


def patch_save_ok(monkeypatch):
    # Avoid writing real file; just simulate success
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)


def test_us01_create_valid(monkeypatch): #tests for a valid creation path
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [])

    res = manager.create_new_asset({
        "asset_id": "A1",
        "name": "Laptop",
        "category": "other",
        "value": 123432,
        "status": "available",
        "assigned_to": None,
        "history": []
    })

    assert isinstance(res, Asset) # asserts return value is an object
    assert manager.get_asset_by_id("A1") is not None # asserts that the asset can be retrieved by ID


def test_us01_create_missing_id(monkeypatch): # tests for an invalid input equivalence class where asse_id is missing
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [])

    res = manager.create_new_asset({
        "asset_id": "",
        "name": "Laptop",
        "category": "other",
        "value": 4352,
        "status": "available",
        "assigned_to": None,
        "history": []
    })

    assert res == "error: missing asset_id" #makes sure the error message is this




def test_us01_create_duplicate_id(monkeypatch): # tests for duplicate prevention
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [
        Asset("A1", "Terraced", "property", 500, "available", None, []) #pre loads an asset with id A1
    ])

    res = manager.create_new_asset({ # tries to create another instance of asset with the same id
        "asset_id": "A1",
        "name": "Laptop",
        "category": "other",
        "value": 909090900,
        "status": "available",
        "assigned_to": None,
        "history": []
    })

    assert res == "duplicate asset_id"


def test_us01_create_missing_required_field(monkeypatch): # tests for missing required field, in this case name:
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [])

    res = manager.create_new_asset({
        "asset_id": "A2",
        "category": "property",
        "value": 100,
        "status": "available",
        "assigned_to": None,
        "history": []
    })

    assert res in ["error: missing required fields", "missing required fields"]



def test_us02_get_existing(monkeypatch): # gets asset by id and see if it gets returned
    manager = make_manager(monkeypatch, [
        Asset("A1", "Porsche", "vehicle", 1000000, "available", None, [])
    ])

    a = manager.get_asset_by_id("A1")
    assert a is not None
    assert a.id == "A1"


def test_us02_get_missing(monkeypatch): # tests if missing or invalid id returns None
    manager = make_manager(monkeypatch, [])
    assert manager.get_asset_by_id("dsuhaui9dhs9ad8a") is None




def test_us03_list_empty(monkeypatch): # tests empty list behavior
    manager = make_manager(monkeypatch, [])
    assert manager.list_assets() == "ERROR: NO ASSETS AVAILABLE"


def test_us03_list_many_sorted(monkeypatch): # uses an unsorted input to check if the output is sorted by Id, i.e A1 then B2
    manager = make_manager(monkeypatch, [
        Asset("B2", "House", "property", 200, "available", None, []),
        Asset("A1", "Mansion", "property", 100, "available", None, []),
    ])

    out = manager.list_assets()
    assert out.splitlines()[0].startswith("A1:")
    assert "B2:" in out




def test_us04_update_success(monkeypatch): # tests if updating a field works
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [
        Asset("A1", "Laptop", "other", 100, "available", None, [])
    ])

    ok = manager.update_asset_field("A1", "name", "house")
    assert ok is True
    assert manager.get_asset_by_id("A1").name == "house"


def test_us04_update_missing_asset(monkeypatch): # tests if there is an update failure when an asset doesn't exist
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [])
    assert manager.update_asset_field("A1", "name", "X") is False


def test_us04_update_invalid_field(monkeypatch): # tests if there is an update failure when an asset field is invalid
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [
        Asset("A1", "Watch", "other", 100, "available", None, [])
    ])
    assert manager.update_asset_field("A1", "random_random", "X") is False




def test_us05_delete_success(monkeypatch): #tests if an asset is deleted successfully via Id
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [
        Asset("A1", "PS5", "other", 300, "available", None, [])
    ])

    ok = manager.delete_asset("A1")
    assert ok is True
    assert manager.get_asset_by_id("A1") is None #ensures asset is not retrievable


def test_us05_delete_missing(monkeypatch): # tries to delete an asset that does not exist
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [])
    assert manager.delete_asset("ijsiasiosaninoda") is False




def test_us06_validate_pass(monkeypatch): # tests for valid input passes
    manager = make_manager(monkeypatch, [])
    assert manager.validate_required_fields({
        "name": "BMW",
        "category": "vehicle",
        "value": 100,
        "status": "available",
        "assigned_to": None,
        "history": []
    }) is True


def test_us06_validate_fail_empty_name(monkeypatch): # tests empty required field like name
    manager = make_manager(monkeypatch, [])
    assert manager.validate_required_fields({
        "name": "",
        "category": "other",
        "value": 100,
        "status": "available",
        "assigned_to": None,
        "history": []
    }) is False