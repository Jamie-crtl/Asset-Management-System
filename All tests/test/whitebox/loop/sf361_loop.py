import pytest
from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    # Avoid reading from assets.json during tests
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    return AssetManager()


def test_us10_loop_zero_assets(monkeypatch):
    manager = make_manager(monkeypatch, [])

    results = manager.search_by_name("anything")
    assert results == []


def test_us10_loop_one_asset(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Gaming Mouse", "other", 50, "available"),
    ])

    assert len(manager.search_by_name("mouse")) == 1
    assert manager.search_by_name("keyboard") == []


def test_us10_loop_many_assets(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "HP Laptop", "property", 600, "available"),
        Asset("2", "Lenovo Laptop", "property", 650, "available"),
        Asset("3", "Whiteboard Marker", "other", 3, "available"),
        Asset("4", "Laptop Stand", "property", 20, "available"),
    ])

    results = manager.search_by_name("laptop")
    names = [a.name for a in results]

    assert "HP Laptop" in names
    assert "Lenovo Laptop" in names
    assert "Laptop Stand" in names
    assert "Whiteboard Marker" not in names
