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
