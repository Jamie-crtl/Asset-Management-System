import pytest
from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    return AssetManager()


def test_us11_condition_empty_category(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assert manager.filter_by_category("") == []


def test_us11_condition_invalid_category(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Tablet", "other", 300, "available"),
    ])

    assert manager.filter_by_category("invalid_category") == []


def test_us11_condition_valid_category(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Forklift", "vehicle", 15000, "available"),
        Asset("2", "Warehouse", "property", 500000, "available"),
    ])

    results = manager.filter_by_category("vehicle")

    assert len(results) == 1
    assert results[0].category == "vehicle"

def test_us12_condition_empty_status(monkeypatch):
    manager = make_manager(monkeypatch, [])
    assert manager.filter_by_status("") == []
    assert manager.filter_by_status(None) == []
    assert manager.filter_by_status("   ") == []


def test_us12_condition_invalid_status(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Desk", "property", 200, "available"),
    ])
    assert manager.filter_by_status("ACTIVE") == []  # not in allowed statuses


def test_us12_condition_valid_status(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Laptop", "other", 900, "available"),
        Asset("2", "Car", "vehicle", 12000, "assigned"),
        Asset("3", "Old Phone", "other", 50, "disposed"),
    ])

    results = manager.filter_by_status("assigned")
    assert len(results) == 1
    assert results[0].id == "2"
    assert results[0].status == "assigned"


def test_us18_condition_asset_is_none(monkeypatch):
    manager = make_manager(monkeypatch, [])

    allowed, message = manager.can_assign_asset(None, "alice")
    assert allowed is False
    assert message == "Asset not found"


def test_us18_condition_empty_user(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Laptop", "other", 900, "available"),
    ])

    asset = manager.get_asset_by_id("1")
    allowed, message = manager.can_assign_asset(asset, "")

    assert allowed is False
    assert message == "Valid user is required"


def test_us18_condition_disposed_asset(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Old PC", "other", 50, "disposed"),
    ])

    asset = manager.get_asset_by_id("1")
    allowed, message = manager.can_assign_asset(asset, "alice")

    assert allowed is False
    assert message == "Cannot assign a disposed asset"


def test_us18_condition_already_assigned(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Phone", "other", 500, "assigned", assigned_to="bob"),
    ])

    asset = manager.get_asset_by_id("1")
    allowed, message = manager.can_assign_asset(asset, "alice")

    assert allowed is False
    assert message == "Asset is already assigned"


def test_us18_condition_valid_assignment(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Monitor", "property", 150, "available"),
    ])

    asset = manager.get_asset_by_id("1")
    allowed, message = manager.can_assign_asset(asset, "alice")

    assert allowed is True
    assert message == "OK"
