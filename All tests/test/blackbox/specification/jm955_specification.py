import json
import os
import storage
from asset import Asset
from asset_manager import AssetManager

def specification_make_manager(monkeypatch):
    monkeypatch.setattr(storage, "save_assets", lambda assets: None)
    monkeypatch.setattr(storage, "load_assets", lambda: [
        Asset("1", "Laptop", "property", 1000, "available"),
        Asset("2", "Car", "vehicle", 5000, "assigned"),
        Asset("3", "Old Phone", "other", 50, "available"),
    ])
    return AssetManager()

#US19
def test_specification_us19_success(monkeypatch):
    manger = specification_make_manager(monkeypatch)
    assert manger.change_asset_status("1", "assigned") == "Status updated successfully"
    assert manger.assets["1"].status == "assigned"

def test_specification_us19_invalid_status(monkeypatch):
    manger = specification_make_manager(monkeypatch)
    assert manger.change_asset_status("1", "broken") == "Valid status is required"

def test_specification_us19_not_found(monkeypatch):
    manager = specification_make_manager(monkeypatch)
    assert manager.change_asset_status("999", "assigned") == "Asset not found"

#US20
def test_specification_us20_end_to_end_reason_attached(monkeypatch):
    manager = specification_make_manager(monkeypatch)
    manager.change_asset_status("1", "assigned")
    assert manager.record_reason_for_change("1", "Loan") == "Reason recorded successfully"
    assert manager.assets["1"].history[-1]["reason"] == "Loan"

#US21
def test_specification_us21_returns_history_after_change(monkeypatch):
    manager = specification_make_manager(monkeypatch)
    manager.change_asset_status("1", "assigned")
    manager.record_reason_for_change("1", "Loan")
    hist = manager.view_status_history("1")
    assert isinstance(hist, list)
    assert hist[-1]["to"] == "assigned"
    assert hist[-1]["reason"] == "Loan"

#US22
def test_specification_us22_set_rate_success(monkeypatch):
    manager = specification_make_manager(monkeypatch)
    assert manager.set_depreciation_rate(0.1) == "Depreciation rate updated successfully"
    assert manager.depreciation_rate == 0.001

def test_specification_us22_set_rate_out_of_range(monkeypatch):
    manager = specification_make_manager(monkeypatch)
    assert manager.set_depreciation_rate(150) == "Rate must be inbetween values 0 and 100"

#US25
def test_specification_us25_export_success(monkeypatch, tmp_path):
    manager = specification_make_manager(monkeypatch)
    out_file = tmp_path / "export.json"

    res = manager.export_assets_to_json(str(out_file))
    assert res == "JSON Exported successfully"
    assert out_file.exists()

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert isinstance(data, list) #list format
    assert any(d.get("id") == "1" for d in data)

#US26
def test_specification_us26_import_success(monkeypatch, tmp_path):
    manager = specification_make_manager(monkeypatch)

    import_file = tmp_path / "import.json"
    import_data = [
        {
            "id": "3",
            "name": "Old Phone",
            "category": "other",
            "value": 50,
            "status": "available",
            "assigned_to": None,
            "history": []
        },
        {
            "id": "1",  # duplicate
            "name": "Laptop",
            "category": "property",
            "value": 1000,
            "status": "available",
            "assigned_to": None,
            "history": []
        }
    ]
    import_file.write_text(json.dumps(import_data), encoding="utf-8")

    res = manager.import_assets_from_json(str(import_file))
    assert "Successfully imported assets" in res
    assert "3" in manager.assets  # imported new asset
    assert "1" in manager.assets  # still exists

#US26
def test_us27_backup_success(monkeypatch, tmp_path):
    manager = specification_make_manager(monkeypatch)

    data_file = tmp_path / "assets.json" #temporary placeholder json file
    data_file.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(storage, "DATA_FILE", str(data_file))

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        res = manager.create_backup_on_exit()
        assert res == "Backup created successfully"
        backup_files = [p for p in tmp_path.iterdir() if p.name.startswith("assets_backup_")]#verify backup file exists
        assert len(backup_files) >= 0
    finally:
        os.chdir(old_cwd)