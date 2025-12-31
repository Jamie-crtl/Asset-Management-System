#All test cases for whitebox concolic testing
from asset_manager import AssetManager
from asset import Asset
import storage
import builtins

def make_manager(monkeypatch, assets_list):
    monkeypatch.setattr(storage, "load_assets", lambda: assets_list)
    monkeypatch.setattr(storage, "save_assets", lambda assets: True)
    return AssetManager()


#US34 - Text-based menu system
def test_us34_run_text_menu_options_shown_per_role(monkeypatch):
    manager = make_manager(monkeypatch, [])

    #checks admin role shows admin-only options

    #exit immediately
    # replaces input() to simulate user interaction
    inputs = iter(["0"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # capture printed output for verification
    printed = []
    monkeypatch.setattr(builtins, "print", lambda *args, **kwargs: printed.append(" ".join(map(str, args))))

    manager.run_text_menu(role="admin")

    #admin only lines printed
    assert any("A - Create new asset" in line for line in printed)
    assert any("U - Flag low value assets" in line for line in printed)
