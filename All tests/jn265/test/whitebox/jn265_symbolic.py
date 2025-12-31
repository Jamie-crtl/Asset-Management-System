#All test cases for whitebox symbolic testing
from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()

#US33 - Recover from corrupt file
def test_us33_recover_from_corrupt_file_backup_file_missing_message_returned(monkeypatch, tmp_path):
    manager = make_manager(monkeypatch, [])

    #forces path where main file is corrupted and backup file is missing

    # temporary files created so repo isnt changed
    main_file = tmp_path / "assets.json"
    backup_file = tmp_path / "assets_backup.json"

    main_file.write_text("{test: not valid JSON}")
    #intentionally no backup file

    data = manager.recover_from_corrupt_file(str(main_file), str(backup_file))

    assert data == "Backup file not found"