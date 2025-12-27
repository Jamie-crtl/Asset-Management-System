from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    return AssetManager()


def test_us17_symbolic_any_user_returns_only_matching_assets(monkeypatch):
    # Symbolic idea: "u" can be any user string
    u = "some_user"

    manager = make_manager(monkeypatch, [
        Asset("1", "Laptop", "other", 900, "assigned", assigned_to=u),
        Asset("2", "Desk", "property", 200, "assigned", assigned_to="other_user"),
        Asset("3", "Phone", "other", 500, "available"),
    ])

    results = manager.view_assets_by_user(u)

    # Property: all returned assets must have assigned_to == u (case-insensitive is handled)
    assert all((a.assigned_to or "").lower() == u.lower() for a in results)
    assert [a.id for a in results] == ["1"]


def test_us17_symbolic_case_insensitive_user_match(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Laptop", "other", 900, "assigned", assigned_to="Alice"),
        Asset("2", "Phone", "other", 500, "assigned", assigned_to="alice"),
        Asset("3", "Desk", "property", 200, "assigned", assigned_to="bob"),
    ])

    results = manager.view_assets_by_user("ALICE")
    ids = [a.id for a in results]

    assert set(ids) == {"1", "2"}


def test_us17_symbolic_empty_user_returns_empty(monkeypatch):
    manager = make_manager(monkeypatch, [
        Asset("1", "Laptop", "other", 900, "assigned", assigned_to="alice"),
    ])

    assert manager.view_assets_by_user("") == []
    assert manager.view_assets_by_user(None) == []
    assert manager.view_assets_by_user("   ") == []
