import random
import storage
from asset import Asset
from asset_manager import AssetManager


def random_make_manager(monkeypatch, assets):
    monkeypatch.setattr(storage, "save_assets", lambda assets: None)
    monkeypatch.setattr(storage, "load_assets", lambda: assets)
    return AssetManager()

#US24: flag low value assets - random blackbox technique
def test_random_us24_random_thresholds(monkeypatch):
    assets = []
    for i in range(10):
        assets.append(
            Asset(
                id=f"A{i}",
                name=f"Asset{i}",
                category=random.choice(list(Asset.ALLOWED_CATEGORIES)), #random assets
                value=random.uniform(0, 10000),  #random values
                status="available"
            )
        )

    manager = random_make_manager(monkeypatch, assets)

    for _ in range(30):
        threshold = random.uniform(-100, 10000)
        result = manager.flag_low_value_assets(threshold)

        if isinstance(result, str):
            assert result == "No assets below threshold"
        else:
            assert isinstance(result, list)