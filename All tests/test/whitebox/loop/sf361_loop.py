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


def test_us13_loop_zero_assets(monkeypatch):
    manager = make_manager(monkeypatch, [])

    results = manager.sort_assets(by="name")
    assert results == []


def test_us13_loop_one_asset(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Whiteboard", "property", 120, "available"),
    ])

    results = manager.sort_assets(by="name")
    assert len(results) == 1
    assert results[0].name == "Whiteboard"


def test_us13_loop_many_assets(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Tablet", "other", 400, "available"),
        Asset("2", "Camera", "other", 300, "available"),
        Asset("3", "Laptop", "other", 900, "available"),
    ])

    results = manager.sort_assets(by="value")
    values = [a.value for a in results]

    assert values == [300, 400, 900]


def test_us17_loop_zero_assets(monkeypatch):
    manager = make_manager(monkeypatch, [])
    assert manager.view_assets_by_user("alice") == []


def test_us17_loop_one_asset_matches_user(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Laptop", "other", 900, "assigned", assigned_to="alice"),
    ])

    results = manager.view_assets_by_user("alice")
    assert len(results) == 1
    assert results[0].id == "1"


def test_us17_loop_many_assets_mixed(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Laptop", "other", 900, "assigned", assigned_to="alice"),
        Asset("2", "Car", "vehicle", 12000, "assigned", assigned_to="bob"),
        Asset("3", "Desk", "property", 200, "available"),
        Asset("4", "Phone", "other", 500, "assigned", assigned_to="alice"),
    ])

    results = manager.view_assets_by_user("alice")
    ids = [a.id for a in results]

    assert set(ids) == {"1", "4"}
