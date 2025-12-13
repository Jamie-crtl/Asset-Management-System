from asset import Asset
import storage

class AssetManager:
    def __init__(self):
        self.assets = [] #may require changing later
        self.depreciation_rate = 0.0 #Required for set_depreciation_rate US

    def create_new_asset(self, asset):
        pass
    def delete_asset(self, asset_id):
        pass
    def get_asset_by_id(self, asset_id):
        pass
    def update_asset_field(self, asset_id,field, new_data):
        pass
    def list_assets(self):
        pass
    def change_asset_status(self, asset_id, new_status, reason):
        pass
    def record_reason_for_change(self, asset, old_status, new_status, reason):
        pass
    def view_status_history(self, asset_id):
        pass
    def set_depreciation_rate(self, rate):
        pass
    def calculate_current_value(self, asset_id, years):
        pass
    def flag_low_value_assets(self, threshold):
        pass
    def export_assets_to_json(self, file_path):
        pass
    def import_assets_from_json(self, file_path):
        pass
    def create_backup_on_exit(self):
        pass


# NEED TO ADD ALL FUNCTIONS THAT WE WILL BE IMPLEMENTING
# WE NEED THIS FOR THE REPORT AT THE END