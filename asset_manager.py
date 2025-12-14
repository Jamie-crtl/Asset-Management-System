from asset import Asset
import storage
#hello
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
                status = asset_data["status"],
                history = asset_data["history"]
            )
        except KeyError as e:
            return "missing required fields"
        except Exception as e:
            return str(e)

        self.assets[asset_id] = new_asset
        return new_asset

        self.assets = [] #may require changing later
        self.assets = storage.load_assets() #Loads JSON file assets
        self.depreciation_rate = 0.0 #Required for set_depreciation_rate US

    def delete_asset(self, asset_id):
        pass
    def get_asset_by_id(self, asset_id):
        pass
    def update_asset_field(self, asset_id,field, new_data):
        pass
    def list_assets(self):
        pass
    def change_asset_status(self, asset_id, new_status):
        pass
    def record_reason_for_change(self, asset_id, reason):
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

    def search_by_name(self, query: str):
        pass
    def filter_by_category(self, category: str):
        pass
    def filter_by_status(self, status: str):
        pass
    def sort_assets(self, by: str = "name", descending: bool = False):
        pass
    def filter_by_value_range(self, min_value: float, max_value: float):
        pass
    def assign_asset_to_user(self, asset_id: str, user: str):
        pass
    def unassign_asset(self, asset_id: str):
        pass
    def view_assets_by_user(self, user: str):
        pass
    def can_assign_asset(self, asset, user: str):
        pass

    def create_inventory_summary(self, assets):
        pass
    def get_assets_per_user(self, asset_id, assets):
        pass
    def create_depreciation_comparison(self, assets):
        pass
    def log_crud_action(self, action, asset_id, user_id=None):
        pass
    def display_error_message(self, message):
        pass
    def recover_from_corrupt_file(self, filename):
        pass
    def run_text_menu(self):
        pass
    def config_file_support(self, config_file):
        pass
    def help_command(self):
        pass




# NEED TO ADD ALL FUNCTIONS THAT WE WILL BE IMPLEMENTING
# WE NEED THIS FOR THE REPORT AT THE END