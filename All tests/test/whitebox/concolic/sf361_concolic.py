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
