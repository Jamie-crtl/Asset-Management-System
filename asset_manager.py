from asset import Asset
import storage
import datetime
import json
import shutil

class AssetManager:
    def __init__(self):
        loaded_assets = storage.load_assets()  # this returns a LIST from storage.py
        self.assets = {a.id: a for a in loaded_assets}  # convert to DICT for fast lookup
        self.depreciation_rate = 0.0

    def create_new_asset(self, asset_data):
        asset_id = asset_data.get("asset_id")
        if not asset_id:
            return "error: missing asset_id"
        if asset_id in self.assets:
            return "duplicate asset_id"
        if not self.validate_required_fields(asset_data):
            return "error: missing required fields"
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



    def delete_asset(self, asset_id):
        if asset_id not in self.assets:
            return False
        del self.assets[asset_id]
        return True

    def get_asset_by_id(self, asset_id):
        if asset_id in self.assets:
            return self.assets[asset_id]
        else:
            return None

    def update_asset_field(self, asset_id,field, new_data):
        if asset_id not in self.assets:
            return False
        asset = self.assets[asset_id]
        allowed_fields = ["name","category","value","status","assigned_to","history"]
        if field not in allowed_fields:
            return False

        setattr(asset, field, new_data)
        return True

    def list_assets(self):
        if not self.assets:
            return "ERROR: NO ASSETS AVAILABLE"
        lines = []
        for asset_id in sorted(self.assets.keys()):
            asset = self.assets[asset_id]
            lines.append(f"{asset_id}: {asset.name} {asset.category} {asset.value}")
        return "\n".join(lines)

    def validate_required_fields(self, asset_data):
        required_fields = ["name","category","value","status","assigned_to","history"]
        for field in required_fields:
            if field not in asset_data:
                return False
            if asset_data[field] is None:
                return False
            if asset_data[field] == "":
                return False
        return True


    def change_asset_status(self, asset_id, new_status):
        if asset_id is None:
            return "Valid asset_id is required"
        if new_status is None:
            return "Valid status is required"

        asset_id = str(asset_id).strip()
        new_status = str(new_status).strip().lower()

        if new_status not in Asset.ALLOWED_STATUSES:
            return "Valid status is required"

        assets = self.assets.values() if isinstance(self.assets, dict) else self.assets  # reads from self.assets

        asset = None
        for a in assets:
            if str(a.id).strip() == asset_id:
                asset = a
                break

        if asset is None:
            return "Asset not found"

        if asset.status == new_status:
            return "Status already set"

        old_status = asset.status
        asset.status = new_status
        asset.history.append({"from": old_status, "to": new_status})

        try:
            storage.save_assets(list(self.assets.values()) if isinstance(self.assets, dict) else self.assets)
        except Exception:
            pass

        return "Status updated successfully"

    def record_reason_for_change(self, asset_id, reason):
        if asset_id is None:
            return "Valid asset_id is required"
        if reason is None:
            return "Valid reason is required"

        asset_id = str(asset_id).strip()
        reason = str(reason).strip()

        if reason == "":
            return "Valid reason is required"

        assets = self.assets.values() if isinstance(self.assets, dict) else self.assets

        asset = None
        for a in assets:
            if str(a.id).strip() == asset_id:
                asset = a
                break

        if asset is None:
            return "Asset not found"

        if not asset.history:
            return "No status change to add a reason for"

        asset.history[-1]["reason"] = reason # Adds a reason to latest reason state

        try:
            storage.save_assets(list(self.assets.values()) if isinstance(self.assets, dict) else self.assets)
        except Exception:
            pass

        return "Reason recorded successfully"

    def view_status_history(self, asset_id):
        if asset_id is None:
            return "Valid asset_id is required."

        asset_id = str(asset_id).strip()

        assets = self.assets.values() if isinstance(self.assets, dict) else self.assets

        asset = None
        for a in assets:
            if str(a.id).strip() == asset_id:
                asset = a
                break

        if asset is None:
            return "Asset not found"

        if not asset.history:
            return "No status history available"

        return asset.history

    def set_depreciation_rate(self, rate):
        if rate is None:
            return "Valid rate is required"

        try:
            rate = float(rate)
        except Exception:
            return "Valid rate is required"

        if rate < 0 or rate > 100:
            return "Rate must be inbetween values 0 and 100" # needs to be a valid integer

        self.depreciation_rate = rate / 100.0  # 0.0 – 1.0
        return "Depreciation rate updated successfully"

    def calculate_current_value(self, asset_id, years):
        if asset_id is None:
            return "Valid asset_id is required"
        if years is None:
            return "Valid years is required"

        asset_id = str(asset_id).strip()

        try:
            years = int(years)
        except Exception:
            return "Valid years is required"

        if years < 0:
            return "Years must be 0 or greater"

        asset = self.assets.get(asset_id)
        if asset is None:
            return "Asset not found"

        try:
            base_value = float(asset.value)
        except Exception:
            return "Asset value is invalid"

        if base_value < 0:
            return "Asset value is invalid"

        current_value = base_value * ((1 - self.depreciation_rate) ** years) # Depreciation calculation: value * (1 - rate)^years

        if current_value < 0:
            current_value = 0.0

        return round(current_value, 2)

    def flag_low_value_assets(self, threshold):
        if threshold is None:
            return "Valid threshold is required"

        try:
            threshold = float(threshold)
        except Exception:
            return "Valid threshold is required"

        if threshold < 0:
            return "Threshold must be 0 or greater"

        low_assets = []
        for asset_id, asset in self.assets.items():
            try:
                v = float(asset.value)
            except Exception:
                continue  # continues even if invalid assets present

            if v < threshold:
                low_assets.append(asset_id)

        if not low_assets:
            return "No assets below threshold"

        return low_assets

    def export_assets_to_json(self, file_path):
        if not file_path:
            return "Valid file_path is required"

        file_path = str(file_path).strip()
        if file_path == "":
            return "Valid file_path is required"

        data = []
        for a in self.assets.values():
            data.append({
                "id": a.id,
                "name": a.name,
                "category": a.category,
                "value": a.value,
                "status": a.status,
                "assigned_to": a.assigned_to,
                "history": a.history
            })

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return "JSON Exported successfully"

    def import_assets_from_json(self, file_path):
        if not file_path:
            return "Valid file_path is required"

        file_path = str(file_path).strip()
        if file_path == "":
            return "Valid file_path is required"

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        imported = 0
        for item in data:
            asset_id = str(item.get("id", "")).strip()
            if asset_id == "" or asset_id in self.assets:
                continue

            new_asset = Asset(
                id=asset_id,
                name=item.get("name", ""),
                category=item.get("category", ""),
                value=item.get("value", 0),
                status=item.get("status", ""),
                assigned_to=item.get("assigned_to"),
                history=item.get("history", [])
            )
            self.assets[asset_id] = new_asset
            imported += 1

        storage.save_assets(list(self.assets.values())) # persist into storage file
        return "Successfully imported assets"

    def create_backup_on_exit(self):
        data_file = getattr(storage, "DATA_FILE", "assets.json")
        backup_file = "assets_backup.json"

        storage.save_assets(list(self.assets.values()))# Ensures storage file exists by saving current state

        shutil.copyfile(data_file, backup_file)
        return "Backup created successfully"

    def search_by_name(self, query: str):
        # Case-insensitive substring search on asset name
        q = (query or "").strip().lower()
        if not q:
            return []

        results = []
        for asset in self.assets.values():
            if q in (asset.name or "").lower():
                results.append(asset)

        return results

    def filter_by_category(self, category: str):
        # Filter assets by valid category
        c = (category or "").strip().lower()
        if not c:
            return []

        if c not in Asset.ALLOWED_CATEGORIES:
            return []

        return [
            asset for asset in self.assets.values()
            if (asset.category or "").lower() == c
        ]

    def filter_by_status(self, status: str):
        # Filter assets by valid status
        s = (status or "").strip().lower()
        if not s:
            return []

        if s not in Asset.ALLOWED_STATUSES:
            return []

        return [
            asset for asset in self.assets.values()
            if (asset.status or "").lower() == s
        ]

    def sort_assets(self, by: str = "name", descending: bool = False):
        # Normalise sort field
        by = (by or "").strip().lower()

        # Choose how each asset is compared during sorting
        if by == "name":
            key_func = lambda a: (a.name or "").lower()
        elif by == "value":
            key_func = lambda a: float(a.value)
        elif by == "category":
            key_func = lambda a: (a.category or "").lower()
        elif by == "status":
            key_func = lambda a: (a.status or "").lower()
        else:
            return []  # Invalid sort field

        # Sort and return assets
        try:
            return sorted(list(self.assets.values()), key=key_func, reverse=descending)
        except Exception:
            return []

    def filter_by_value_range(self, min_value: float, max_value: float):
        # Convert inputs to numbers
        try:
            min_v = float(min_value)
            max_v = float(max_value)
        except (TypeError, ValueError):
            return []

        # Invalid range
        if min_v > max_v:
            return []

        results = []

        for asset in self.assets.values():
            try:
                value = float(asset.value)
            except (TypeError, ValueError):
                continue  # Skip assets with invalid values

            if min_v <= value <= max_v:
                results.append(asset)

        return results

    def assign_asset_to_user(self, asset_id: str, user: str):
        # Basic input validation
        if asset_id is None or user is None:
            return False, "Valid asset_id and user are required"

        asset_id = str(asset_id).strip()
        user = str(user).strip()

        if asset_id == "" or user == "":
            return False, "Valid asset_id and user are required"

        # Retrieve asset
        asset = self.get_asset_by_id(asset_id)
        if asset is None:
            return False, "Asset not found"

        # Business rules (centralised)
        allowed, message = self.can_assign_asset(asset, user)
        if not allowed:
            return False, message

        # Perform assignment
        asset.assigned_to = user
        asset.status = "assigned"
        asset.history.append({
            "action": "assign",
            "user": user,
            "timestamp": str(datetime.datetime.now())
        })

        # Save changes
        try:
            storage.save_assets(list(self.assets.values()))
        except Exception:
            pass

        return True, "Asset assigned successfully"

    def unassign_asset(self, asset_id: str):
        pass
    def view_assets_by_user(self, user: str):
        pass
    def can_assign_asset(self, asset, user: str):
        if asset is None:
            return False, "Asset not found"

        u = (user or "").strip()
        if u == "":
            return False, "Valid user is required"

        # Business rules
        if asset.status == "disposed":
            return False, "Cannot assign a disposed asset"

        if asset.assigned_to is not None:
            return False, "Asset is already assigned"

        # if status is inconsistent, still block
        if asset.status not in ["available"]:
            return False, "Asset is not available for assignment"

        return True, "OK"

    def create_inventory_summary(self, assets):
        if not isinstance(assets, list):
            return "Assets must be provided in a list"

        summary = {}

        for asset in assets:

            if asset is None:
                return "Asset not found"

            if not hasattr(asset, "category") or not hasattr(asset, "status"):
                return "Asset is missing category and/or status"

            if not hasattr(asset, "value") or asset.value < 0:
                return "Asset is missing value or has negative value"

            category = asset.category
            status = asset.status
            value = asset.value

            if category not in summary:
                summary[category] = {}

            if status not in summary[category]:
                summary[category][status] = {
                    "count": 0,
                    "total_value": 0.0
                }

            summary[category][status]["count"] += 1
            summary[category][status]["total_value"] += value

        return summary

    def get_assets_per_user(self, asset_id, assets):
        if not isinstance(assets, list):
            return "Assets must be provided in a list"

        asset_list = []

        for asset in assets:

            if asset is None:
                return "Asset not found"

            if not hasattr(asset, "assigned_to"):
                return "Missing assignee"

            assigned_user = asset.assigned_to if asset.assigned_to else "Unassigned"

            asset_list.append({
                "asset_id": asset.id,
                "name": asset.name,
                "category": asset.category,
                "status": asset.status,
                "assigned_to": assigned_user
            })

        return asset_list

    def create_depreciation_comparison(self, assets):
        if not isinstance(assets, list):
            return "Assets must be provided in a list"

        report = []

        for asset in assets:

            # defensive programming
            if asset is None:
                return "Asset not found"

            if not hasattr(asset, "history") or not hasattr(asset, "value"):
                return "Asset is missing history and/or value"

            if not asset.history:
                return "No report history available"

            original_value = asset.history[0]
            current_value = asset.value

            # defensive programming
            if original_value <= 0 or current_value < 0:
                return "Asset has no value"

            # calculate percentage drop
            depreciation = original_value - current_value
            percentage_drop = (depreciation / original_value) * 100

            # enter asset into depreciation comparison report
            report.append({
                "asset_id": asset.id,
                "name": asset.name,
                "category": asset.category,
                "original_value": original_value,
                "current_value": current_value,
                "percentage_drop": round(percentage_drop, 2)
            })

        # sort report by % drop
        report.sort(key=lambda x: x["percentage_drop"], reverse=True)

        return report

    def log_crud_action(self, action, asset_id):

        if action not in ["CREATE", "READ", "UPDATE", "DELETE"]:
            return self.display_error_message("Invalid CRUD action")

        if asset_id is None:
            return self.display_error_message("Asset not found")

        # logs date and time of CRUD action
        timestamp = datetime.datetime.now()

        action_entry = f"{timestamp}, ID: {asset_id}, {action}\n"

        with open("crud_log.txt", "a") as f:
            f.write(action_entry)

        return f"CRUD action successfully logged at {timestamp}"

    def display_error_message(self, message):
        print(f"ERROR: {message}")
        return message

    def recover_from_corrupt_file(self, filename, backup_file):
        try:
            with open(filename, "r") as f:
                return json.load(f)

        #detects JSON decode errors
        except json.JSONDecodeError:
            self.display_error_message("JSON file corrupted, loading backup")

            #loads backup file
            try:
                with open(backup_file, "r") as f:
                    return json.load(f)

            #detects JSON decode errors
            except json.JSONDecodeError:
                return self.display_error_message("Backup file corrupted")

            #checks for backup file existence
            except FileNotFoundError:
                return self.display_error_message("Backup file not found")

        #checks for file existence
        except FileNotFoundError:
            return self.display_error_message("File not found")

    def run_text_menu(self):
        pass
    def config_file_support(self, config_file):
        pass
    def help_command(self):
        pass




# NEED TO ADD ALL FUNCTIONS THAT WE WILL BE IMPLEMENTING
# WE NEED THIS FOR THE REPORT AT THE END