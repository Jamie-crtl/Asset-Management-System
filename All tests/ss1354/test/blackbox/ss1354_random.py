import random
from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list): # creates an AssetManager instance without touching the real fs
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()


def test_us04_random_robustness_test(monkeypatch): # repeatedly updates each asset with random values, to see if they succeed or not (stability)
    assets = []
    for i in range(10):
        assets.append(Asset(str(i), f"Asset{i}", "other", random.randint(0, 1000), "available", None, []))

    m = make_manager(monkeypatch, assets)

    for i in range(10):
        ok = m.update_asset_field(str(i), "value", random.randint(0, 2000))
        assert ok is True


def test_us03_random_list_contains_all_ids(monkeypatch): #verifies that every asset Id appears in the output without being dropped
    assets = []
    for i in range(10):
        assets.append(Asset(str(i), f"Asset{i}", "other", 1, "available", None, []))

    m = make_manager(monkeypatch, assets)
    out = m.list_assets()

    for i in range(10):
        assert f"{i}:" in out