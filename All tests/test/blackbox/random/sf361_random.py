import random
from asset_manager import AssetManager
from asset import Asset
import storage


def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    return AssetManager()


def test_us14_random_value_ranges(monkeypatch):
    assets = []
    for i in range(20):
        value = random.randint(0, 1000)
        assets.append(
            Asset(str(i), f"Asset{i}", "other", value, "available")
        )

    manager = make_manager(monkeypatch, assets)

    min_v = random.randint(0, 500)
    max_v = random.randint(min_v, 1000)

    results = manager.filter_by_value_range(min_v, max_v)

    for asset in results:
        assert min_v <= asset.value <= max_v
