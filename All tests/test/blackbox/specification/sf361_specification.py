import pytest
from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    # Avoid reading from assets.json during tests
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    return AssetManager()


def test_us10_search_by_name_case_insensitive(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Dell Laptop", "property", 500, "available"),
        Asset("2", "Office Chair", "property", 80, "available"),
        Asset("3", "lApToP Bag", "other", 25, "available"),
    ])

    results = manager.search_by_name("laptop")
    names = [a.name for a in results]

    assert "Dell Laptop" in names
    assert "lApToP Bag" in names
    assert "Office Chair" not in names


def test_us10_search_by_name_substring_match(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Apple iPhone", "other", 900, "available"),
        Asset("2", "Android Phone", "other", 300, "available"),
        Asset("3", "Desk", "property", 120, "available"),
    ])

    results = manager.search_by_name("phone")
    names = [a.name for a in results]

    assert "Apple iPhone" in names
    assert "Android Phone" in names
    assert "Desk" not in names


def test_us10_search_by_name_empty_query_returns_empty_list(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Monitor", "property", 150, "available"),
    ])

    assert manager.search_by_name("") == []
    assert manager.search_by_name(None) == []
    assert manager.search_by_name("   ") == []
