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


import random
import string


def test_us18_random_assignment_rules(monkeypatch):
    assets = []
    statuses = ["available", "assigned", "disposed"]

    for i in range(20):
        status = random.choice(statuses)
        assigned_to = None
        if status == "assigned":
            assigned_to = "user" + str(i)

        assets.append(
            Asset(str(i), f"Asset{i}", "other", random.randint(1, 1000), status, assigned_to)
        )

    manager = make_manager(monkeypatch, assets)

    for asset in assets:
        user = "".join(random.choices(string.ascii_letters, k=5))
        allowed, message = manager.can_assign_asset(asset, user)

        if asset.status == "disposed":
            assert allowed is False
        elif asset.assigned_to is not None:
            assert allowed is False
        else:
            assert allowed in [True, False]  # should never crash
