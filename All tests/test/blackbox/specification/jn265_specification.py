#All test cases for blackbox specification testing
from asset_manager import AssetManager
from asset import Asset
import storage
import builtins

def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()


#US28 - Create Inventory Summary
def test_us28_create_inventory_summary_by_category_and_status(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [
        Asset("1", "Desk", "property", 200, "available"),
        Asset("2", "Chair", "property", 80, "available"),
        Asset("3", "Car", "vehicle", 10000, "assigned"),
        Asset("4", "Old Phone", "other", 25, "disposed"),
        Asset("5", "Spare Car", "vehicle", 5000, "assigned")
    ]

    summary = manager.create_inventory_summary(assets)

    #values are constructed correctly
    assert summary["property"]["available"]["count"] == 2
    assert summary["property"]["available"]["total_value"] == 280

    assert summary["vehicle"]["assigned"]["count"] == 2
    assert summary["vehicle"]["assigned"]["total_value"] == 15000

    assert summary["other"]["disposed"]["count"] == 1
    assert summary["other"]["disposed"]["total_value"] == 25

def test_us28_create_inventory_summary_single_asset(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [Asset("1", "Desk", "property", 200, "available")]

    summary = manager.create_inventory_summary(assets)

    #example summary with one asset description
    assert summary == {
        "property": {
            "available": {
                "count": 1,
                "total_value": 200
            }
        }
    }

def test_us28_create_inventory_summary_empty_list(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = []

    summary = manager.create_inventory_summary(assets)

    assert summary == {}


#US29 - View assets per user
def test_us29_get_assets_per_user_returns_list_of_dicts(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [
        Asset("1", "Desk", "property", 200, "assigned", assigned_to="Alice"),
        Asset("2", "Car", "vehicle", 10000, "assigned", assigned_to="Bob")
    ]

    result = manager.get_assets_per_user(assets)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], dict)

    assert result[0]["asset_id"] == "1"
    assert result[0]["name"] == "Desk"
    assert result[0]["category"] == "property"
    assert result[0]["status"] == "assigned"
    assert result[0]["assigned_to"] == "Alice"


def test_us29_get_assets_per_user_unassigned_label(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [
        Asset("1", "Laptop", "other", 900, "available", assigned_to=None),
        Asset("2", "Monitor", "property", 150, "available", assigned_to="")
    ]

    result = manager.get_assets_per_user(assets)

    assigned_values = [r["assigned_to"] for r in result]
    #checks blank values are given unassigned
    assert assigned_values == ["Unassigned", "Unassigned"]


#US30 - Depreciation comparison report
def test_us30_create_depreciation_comparison_sorted_descending(monkeypatch):
    manager = make_manager(monkeypatch, [])

    assets = [
        Asset("1", "Desk", "property", 50, "available", history=[100]), #50% drop
        Asset("2", "Car", "vehicle", 9000, "assigned", history=[10000]), #10% drop
        Asset("3", "Laptop", "other", 0, "disposed", history=[100]) #100% drop
    ]

    report = manager.create_depreciation_comparison(assets)

    assert isinstance(report, list)
    percentage_drops = [item["percentage_drop"] for item in report]

    #ensures sorted by descending percentage drop
    assert percentage_drops == sorted(percentage_drops, reverse=True)
    assert report[0]["asset_id"] == "3"
    assert report[-1]["asset_id"] == "2"


def test_us30_create_depreciation_comparison_calculation(monkeypatch):
    manager = make_manager(monkeypatch, [])

    asset = Asset("1", "Desk", "property", 75, "available", history=[100])

    report = manager.create_depreciation_comparison([asset])

    #ensures calculation is correct
    assert report[0]["percentage_drop"] == 25.0
    assert report[0]["original_value"] == 100
    assert report[0]["current_value"] == 75


#US31 - Log CRUD actions
def test_us31_log_crud_action_write_to_file(monkeypatch, tmp_path):
    manager = make_manager(monkeypatch, [])

    #temporary file as not to overwrite crud_log.txt
    log_file = tmp_path / "crud_log.txt"
    real_open = builtins.open

    #redirects request to open crud_log to temporary file
    def fake_open(name, mode="r", *args, **kwargs):
        if name == "crud_log.txt":
            return real_open(log_file, mode, *args, **kwargs)
        return real_open(name, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)

    #ensures entry is successfully logged
    log = manager.log_crud_action("CREATE", "1")
    assert "CRUD action successfully logged at" in log

    #ensures information is formatted correctly
    content = log_file.read_text()
    assert "ID: 1" in content
    assert "CREATE" in content


#US32 - Display error messages
def test_us32_display_error_message_returns_message(monkeypatch):
    manager = make_manager(monkeypatch, [])

    result = manager.display_error_message("Invalid input")
    #confirms message return
    assert result == "Invalid input"


#US35 - Config file support
def test_us35_config_file_support_missing_file_loads_defaults(monkeypatch, tmp_path):
    manager = make_manager(monkeypatch, [])

    missing_config = tmp_path / "does_not_exist.json"

    config = manager.config_file_support(str(missing_config))

    #checks default values have been implemented
    assert config["data_file"] == "assets.json"
    assert config["backup_file"] == "assets_backup.json"
    assert config["depreciation_rate"] == 0.0
    assert config["max_backups"] == 5