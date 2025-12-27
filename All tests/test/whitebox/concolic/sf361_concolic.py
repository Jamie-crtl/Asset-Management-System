import pytest
from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    return AssetManager()


def test_us12_concolic_path_empty_input(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Monitor", "property", 150, "available"),
    ])

    # Path: early return on empty
    assert manager.filter_by_status("") == []


def test_us12_concolic_path_invalid_status(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Monitor", "property", 150, "available"),
    ])

    # Path: early return on invalid status
    assert manager.filter_by_status("invalid_status") == []


def test_us12_concolic_path_valid_status(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Monitor", "property", 150, "available"),
        Asset("2", "Car", "vehicle", 9000, "assigned"),
        Asset("3", "Warehouse", "property", 100000, "assigned"),
    ])

    # Path: valid status → loop/filter path
    results = manager.filter_by_status("assigned")
    ids = [a.id for a in results]

    assert set(ids) == {"2", "3"}


def test_us15_concolic_path_invalid_input(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Monitor", "property", 150, "available"),
    ])

    success, message = manager.assign_asset_to_user("", "")
    assert success is False
    assert message == "Valid asset_id and user are required"


def test_us15_concolic_path_asset_not_found(monkeypatch):
    manager = make_manager(monkeypatch, [])

    success, message = manager.assign_asset_to_user("1", "alice")
    assert success is False
    assert message == "Asset not found"


def test_us15_concolic_path_disposed(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Printer", "other", 100, "disposed"),
    ])

    success, message = manager.assign_asset_to_user("1", "alice")
    assert success is False
    assert message == "Cannot assign a disposed asset"


def test_us15_concolic_path_success(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Keyboard", "other", 40, "available"),
    ])

    success, message = manager.assign_asset_to_user("1", "alice")

    assert success is True
    assert message == "Asset assigned successfully"
