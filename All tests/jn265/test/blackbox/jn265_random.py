#All test cases for blackbox random testing
from asset_manager import AssetManager
import storage
import random
import json

def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()


#US35 - Config file support
def test_us35_config_file_support_random_depreciation_rates(monkeypatch, tmp_path):
    manager = make_manager(monkeypatch, [])

    for _ in range(10):
        #range of valid and invalid rates
        rate = random.uniform(-2.0, 2.0)

        config_file = tmp_path / "assets.json"
        config_file.write_text(json.dumps({"depreciation_rate": rate}))

        #reset before each loop
        manager.depreciation_rate = 0.0

        manager.config_file_support(str(config_file))

        #valid rates set, invalid rates set to default
        if 0 <= rate <= 1:
            assert manager.depreciation_rate == rate
        else:
            assert manager.depreciation_rate == 0.0
