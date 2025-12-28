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


def test_us01_create_valid(monkeypatch):
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [])

    res = manager.create_new_asset({
        "asset_id": "A1",
        "name": "Laptop",
        "category": "property",
        "value": 100,
        "status": "available",
        "assigned_to": None,
        "history": []
    })

    assert isinstance(res, Asset)
    assert manager.get_asset_by_id("A1") is not None


def test_us01_create_missing_id(monkeypatch):
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [])

    res = manager.create_new_asset({
        "asset_id": "",
        "name": "Laptop",
        "category": "property",
        "value": 100,
        "status": "available",
        "assigned_to": None,
        "history": []
    })

    assert res == "error: missing asset_id"




def test_us01_create_duplicate_id(monkeypatch):
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [
        Asset("A1", "Existing", "property", 50, "available", None, [])
    ])

    res = manager.create_new_asset({
        "asset_id": "A1",
        "name": "Laptop",
        "category": "property",
        "value": 100,
        "status": "available",
        "assigned_to": None,
        "history": []
    })

    assert res == "duplicate asset_id"


def test_us01_create_missing_required_field(monkeypatch):
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [])

    res = manager.create_new_asset({
        "asset_id": "A2",
        # missing name
        "category": "property",
        "value": 100,
        "status": "available",
        "assigned_to": None,
        "history": []
    })

    assert res in ["error: missing required fields", "missing required fields"]



def test_us02_get_existing(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("A1", "Laptop", "property", 100, "available", None, [])
    ])

    a = manager.get_asset_by_id("A1")
    assert a is not None
    assert a.id == "A1"


def test_us02_get_missing(monkeypatch):
    manager = make_manager(monkeypatch, [])
    assert manager.get_asset_by_id("NOPE") is None




def test_us03_list_empty(monkeypatch):
    manager = make_manager(monkeypatch, [])
    assert manager.list_assets() == "ERROR: NO ASSETS AVAILABLE"


def test_us03_list_many_sorted(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("B2", "Desk", "property", 200, "available", None, []),
        Asset("A1", "Laptop", "property", 100, "available", None, []),
    ])

    out = manager.list_assets()
    # should be sorted by id -> A1 before B2
    assert out.splitlines()[0].startswith("A1:")
    assert "B2:" in out




def test_us04_update_success(monkeypatch):
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [
        Asset("A1", "Laptop", "property", 100, "available", None, [])
    ])

    ok = manager.update_asset_field("A1", "name", "NewName")
    assert ok is True
    assert manager.get_asset_by_id("A1").name == "NewName"


def test_us04_update_missing_asset(monkeypatch):
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [])
    assert manager.update_asset_field("A1", "name", "X") is False


def test_us04_update_invalid_field(monkeypatch):
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [
        Asset("A1", "Laptop", "property", 100, "available", None, [])
    ])
    assert manager.update_asset_field("A1", "not_a_field", "X") is False




def test_us05_delete_success(monkeypatch):
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [
        Asset("A1", "Laptop", "property", 100, "available", None, [])
    ])

    ok = manager.delete_asset("A1")
    assert ok is True
    assert manager.get_asset_by_id("A1") is None


def test_us05_delete_missing(monkeypatch):
    patch_save_ok(monkeypatch)
    manager = make_manager(monkeypatch, [])
    assert manager.delete_asset("NOPE") is False




def test_us06_validate_pass(monkeypatch):
    manager = make_manager(monkeypatch, [])
    assert manager.validate_required_fields({
        "name": "Laptop",
        "category": "property",
        "value": 100,
        "status": "available",
        "assigned_to": None,
        "history": []
    }) is True


def test_us06_validate_fail_empty_name(monkeypatch):
    manager = make_manager(monkeypatch, [])
    assert manager.validate_required_fields({
        "name": "",
        "category": "property",
        "value": 100,
        "status": "available",
        "assigned_to": None,
        "history": []
    }) is False