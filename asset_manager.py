from asset import Asset
import storage

class AssetManager:
    def __init__(self):
        self.assets = {} #may require changing later, currently using a dictionary

    def create_new_asset(self, asset_data):
        asset_id = asset_data.get("asset_id")
        if not asset_id:
            return "error: missing asset_id"
        if asset_id in self.assets:
            return "duplicate asset_id"
        try:
            new_asset = Asset(
                id = asset_data["asset_id"],
                name = asset_data["name"],
                category = asset_data["category"],
                value = asset_data["value"],
                status = asset_data["status"]
            )
        except KeyError as e:
            return "missing required fields"
        except Exception as e:
            return str(e)

        self.assets[asset_id] = new_asset
        return new_asset


    def delete_asset(self, asset_id):
        pass
    def get_asset_by_id(self, asset_id):
        pass
    def update_asset_field(self, asset_id,field, new_data):
        pass
    def list_assets(self):
        pass


# NEED TO ADD ALL FUNCTIONS THAT WE WILL BE IMPLEMENTING
# WE NEED THIS FOR THE REPORT AT THE END