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

def test_us11_filter_by_category_valid_category(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Office Desk", "property", 200, "available"),
        Asset("2", "Company Car", "vehicle", 12000, "assigned"),
        Asset("3", "Laptop", "other", 900, "available"),
    ])

    results = manager.filter_by_category("property")
    names = [a.name for a in results]

    assert names == ["Office Desk"]


def test_us11_filter_by_category_case_insensitive(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Car", "vehicle", 8000, "available"),
        Asset("2", "Bike", "vehicle", 300, "available"),
    ])

    results = manager.filter_by_category("VeHiClE")
    assert len(results) == 2


def test_us11_filter_by_category_invalid_category(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Printer", "other", 150, "available"),
    ])

    assert manager.filter_by_category("electronics") == []


def test_us11_filter_by_category_empty_input(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Monitor", "property", 180, "available"),
    ])

    assert manager.filter_by_category("") == []
    assert manager.filter_by_category(None) == []


def test_us13_sort_by_name_ascending(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Chair", "property", 50, "available"),
        Asset("2", "Laptop", "other", 900, "available"),
        Asset("3", "Desk", "property", 200, "available"),
    ])

    results = manager.sort_assets(by="name", descending=False)
    names = [a.name for a in results]

    assert names == ["Chair", "Desk", "Laptop"]


def test_us13_sort_by_value_descending(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Printer", "other", 150, "available"),
        Asset("2", "Server", "other", 5000, "available"),
        Asset("3", "Mouse", "other", 25, "available"),
    ])

    results = manager.sort_assets(by="value", descending=True)
    values = [a.value for a in results]

    assert values == [5000, 150, 25]


def test_us13_sort_invalid_field_returns_empty_list(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Monitor", "property", 180, "available"),
    ])

    assert manager.sort_assets(by="invalid") == []


def test_us14_filter_by_value_range_valid(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Laptop", "other", 900, "available"),
        Asset("2", "Chair", "property", 80, "available"),
        Asset("3", "Desk", "property", 200, "available"),
    ])

    results = manager.filter_by_value_range(100, 500)
    names = [a.name for a in results]

    assert "Desk" in names
    assert "Laptop" not in names
    assert "Chair" not in names


def test_us14_filter_by_value_range_boundary_values(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Monitor", "other", 150, "available"),
        Asset("2", "Keyboard", "other", 50, "available"),
    ])

    results = manager.filter_by_value_range(50, 150)
    values = [a.value for a in results]

    assert 50 in values
    assert 150 in values


def test_us14_filter_by_value_range_invalid_range(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Server", "other", 5000, "available"),
    ])

    # min > max should fail safely
    assert manager.filter_by_value_range(1000, 100) == []


def test_us14_filter_by_value_range_invalid_inputs(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Router", "other", 120, "available"),
    ])

    assert manager.filter_by_value_range("low", 500) == []
    assert manager.filter_by_value_range(100, "high") == []
