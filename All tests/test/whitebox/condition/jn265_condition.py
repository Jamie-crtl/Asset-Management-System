#All test cases for whitebox condition testing
import json
from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()


#US28 - Create inventory summary
def test_us28_create_inventory_summary_not_list(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assert manager.create_inventory_summary("test: not a list") == "Assets must be provided in a list"


def test_us28_create_inventory_summary_asset_is_none(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assert manager.create_inventory_summary([None]) == "Asset not found"


def test_us28_create_inventory_summary_negative_asset_value(monkeypatch):
    manager = make_manager(monkeypatch, [])
    asset = Asset("1", "Desk", "property", 10, "available")
    #bypasses Asset class
    asset.value = -1
    assert manager.create_inventory_summary([asset]) == "Asset is missing value or has negative value"


#US29 - View assets per user
def test_us29_get_assets_per_user_not_list(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assert manager.get_assets_per_user("test: not a list") == "Assets must be provided in a list"

def test_us29_get_assets_per_user_asset_is_none(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assert manager.get_assets_per_user([None]) == "Asset not found"


#US30 - Depreciation comparison report
def test_us30_create_depreciation_comparison_not_list(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assert manager.create_depreciation_comparison("test: not a list") == "Assets must be provided in a list"

def test_us30_create_depreciation_comparison_asset_is_none(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assert manager.create_depreciation_comparison([None]) == "Asset not found"


def test_us30_create_depreciation_comparison_no_history(monkeypatch):
    manager = make_manager(monkeypatch, [])

    asset = Asset("1", "Desk", "property", 50, "available", history=[])

    assert manager.create_depreciation_comparison([asset]) == "No report history available"


def test_us30_create_depreciation_comparison_original_value_invalid(monkeypatch):
    manager = make_manager(monkeypatch, [])

    asset = Asset("1", "Desk", "property", 50, "available", history=[0])

    assert manager.create_depreciation_comparison([asset]) == "Asset has no value"


def test_us30_create_depreciation_comparison_current_value_invalid(monkeypatch):
    manager = make_manager(monkeypatch, [])

    asset = Asset("1", "Desk", "property", 50, "available", history=[100])
    #bypasses Asset class
    asset.value = -1
    assert manager.create_depreciation_comparison([asset]) == "Asset has no value"


#US31 - Log CRUD actions
def test_us31_log_crud_action_invalid_action(monkeypatch):
    manager = make_manager(monkeypatch, [])

    result = manager.log_crud_action("INVALID_ACTION", "1")

    assert result == "Invalid CRUD action"

def test_us31_log_crud_action_asset_is_none(monkeypatch):
    manager = make_manager(monkeypatch, [])

    result = manager.log_crud_action("CREATE", None)

    assert result == "Asset not found"


#US33 - Recover from corrupt file
def test_us33_recover_from_corrupt_file_load_main_file(monkeypatch, tmp_path):
    manager = make_manager(monkeypatch, [])

    #temporary files created so repo isnt changed
    main_file = tmp_path / "assets.json"
    backup_file = tmp_path / "assets_backup.json"

    main_file.write_text(json.dumps([{"id": "1"}]))
    backup_file.write_text(json.dumps([{"id": "backup"}]))

    data = manager.recover_from_corrupt_file(str(main_file), str(backup_file))

    assert data == [{"id": "1"}]


def test_us33_recover_from_corrupt_file_load_backup_when_corrupt(monkeypatch, tmp_path):
    manager = make_manager(monkeypatch, [])

    #temporary files created so repo isnt changed
    main_file = tmp_path / "assets.json"
    backup_file = tmp_path / "assets_backup.json"

    main_file.write_text("{test: not valid JSON}") #input is not JSON
    backup_file.write_text(json.dumps([{"id": "backup"}]))

    data = manager.recover_from_corrupt_file(str(main_file), str(backup_file))

    assert data == [{"id": "backup"}]


def test_us33_recover_from_corrupt_file_backup_file_corrupted_message_returned(monkeypatch, tmp_path):
    manager = make_manager(monkeypatch, [])

    # temporary files created so repo isnt changed
    main_file = tmp_path / "assets.json"
    backup_file = tmp_path / "assets_backup.json"

    #input is not JSON
    main_file.write_text("{test: not valid JSON}")
    backup_file.write_text("{test: also not valid JSON}")

    data = manager.recover_from_corrupt_file(str(main_file), str(backup_file))

    assert data == "Backup file corrupted"


def test_us33_recover_from_corrupt_file_backup_file_missing_message_returned(monkeypatch, tmp_path):
    manager = make_manager(monkeypatch, [])

    # temporary files created so repo isnt changed
    main_file = tmp_path / "assets.json"
    backup_file = tmp_path / "assets_backup.json"

    main_file.write_text("{test: not valid JSON}")
    #intentionally no backup file

    data = manager.recover_from_corrupt_file(str(main_file), str(backup_file))

    assert data == "Backup file not found"


def test_us33_recover_from_corrupt_file_main_file_missing_message_returned(monkeypatch, tmp_path):
    manager = make_manager(monkeypatch, [])

    # temporary files created so repo isnt changed
    main_file = tmp_path / "assets.json"
    backup_file = tmp_path / "assets_backup.json"

    data = manager.recover_from_corrupt_file(str(main_file), str(backup_file))

    assert data == "File not found"

