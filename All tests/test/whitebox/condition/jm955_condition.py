import storage
from asset import Asset
from asset_manager import AssetManager

def condition_make_manager(monkeypatch):
    monkeypatch.setattr(storage, "save_assets", lambda assets: None)
    monkeypatch.setattr(storage, "load_assets", lambda: [
        Asset("1", "Laptop", "property", 1000, "available"),
        Asset("2", "Car", "vehicle", 5000, "assigned")
    ])
    return AssetManager()

#US19
def test_condition_us19_asset_id_none(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    assert manager.change_asset_status(None, "assigned") == "Valid asset_id is required"

def test_condition_us19_same_status(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    assert manager.change_asset_status("1", "available") == "Status already set"

#US20
def test_condition_us20_asset_not_found(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    assert manager.record_reason_for_change("999", "Reason") == "Asset not found"


def test_condition_us20_blank_reason(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    manager.change_asset_status("1", "assigned")
    assert manager.record_reason_for_change("1", "   ") == "Valid reason is required"

def test_condition_us20_no_status_change_yet(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    assert manager.record_reason_for_change("2", "Some reason") == "No status change to add a reason for"


def test_condition_us20_success(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    manager.change_asset_status("1", "assigned")
    res = manager.record_reason_for_change("1", "Issued to new starter")
    assert res == "Reason recorded successfully"
    assert manager.assets["1"].history[-1]["reason"] == "Issued to new starter"

#US22
def test_condition_us22_rate_none(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    assert manager.set_depreciation_rate(None) == "Valid rate is required"

def test_condition_us22_rate_not_number(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    assert manager.set_depreciation_rate("abc") == "Valid rate is required"

#US23
def test_condition_us23_asset_id_none(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    assert manager.calculate_current_value(None, 1) == "Valid asset_id is required"

def test_condition_us23_years_negative(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    manager.set_depreciation_rate(0.1)
    assert manager.calculate_current_value("1", -1) == "Years must be 0 or greater"

# US25
def test_condition_us25_invalid_path(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    assert manager.export_assets_to_json("") == "Valid file_path is required"
    assert manager.export_assets_to_json(None) == "Valid file_path is required"

# US26
def test_condition_us26_file_not_found(monkeypatch):
    manager = condition_make_manager(monkeypatch)
    assert manager.import_assets_from_json("error_test.json") == "File not found"
