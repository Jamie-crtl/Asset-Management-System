from asset import Asset
import storage
import datetime
import json
import os
import shutil

class AssetManager:
    def __init__(self):
        loaded_assets = storage.load_assets()  # this returns a LIST from storage.py
        self.assets = self.load_assets_preventing_duplicates(loaded_assets)  # convert to DICT for fast lookup
        self.depreciation_rate = 0.0

    def persist_data_to_file(self):
        persist = storage.save_assets(list(self.assets.values()))
        if not persist:
            print("Failed to save assets")
        return persist

    def load_assets_preventing_duplicates(self, loaded_assets):
        assets = {}
        for a in loaded_assets:
            if a.id not in assets:
                assets[a.id] = a
        return assets

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
        self.persist_data_to_file()
        return new_asset

    def delete_asset(self, asset_id):
        if asset_id not in self.assets:
            return False
        del self.assets[asset_id]
        self.persist_data_to_file()
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
        self.persist_data_to_file()
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
        required_fields = ["name","category","value","status"]
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

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

        except FileNotFoundError:
            return "File not found"

        except json.JSONDecodeError:
            return "Invalid JSON file"

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

        if not os.path.exists(data_file):
            return "No data file to backup"

        try:
            shutil.copyfile(data_file, backup_file)
            return "Backup created successfully"
        except Exception:
            return "Backup failed"

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
        if asset_id is None:
            return False, "Valid asset_id is required"

        asset_id = str(asset_id).strip()
        if asset_id == "":
            return False, "Valid asset_id is required"

        asset = self.get_asset_by_id(asset_id)
        if asset is None:
            return False, "Asset not found"

        if asset.status == "disposed":
            return False, "Cannot unassign a disposed asset"

        if asset.assigned_to is None:
            return False, "Asset is not assigned"

        old_user = asset.assigned_to
        asset.assigned_to = None
        asset.status = "available"
        asset.history.append({
            "action": "unassign",
            "user": old_user,
            "timestamp": str(datetime.datetime.now())
        })

        try:
            storage.save_assets(list(self.assets.values()))
        except Exception:
            pass

        return True, "Asset unassigned successfully"

    def view_assets_by_user(self, user: str):
        if user is None:
            return []

        u = str(user).strip().lower()
        if u == "":
            return []

        results = []
        for asset in self.assets.values():
            if asset.assigned_to is None:
                continue
            if str(asset.assigned_to).strip().lower() == u:
                results.append(asset)

        return results

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

    def get_assets_per_user(self, assets):
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
                return self.display_error_message("No report history available")

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

    def run_text_menu(self, role):
        while True:
            print("\n Asset Management System")

            #Admin only options
            if role == "admin":
                print("A - Create new asset")
                print("B - List all assets")
                print("C - Delete asset")
                print("D - Update asset field")
                print("E - Assign asset to user")
                print("F - Unassign asset")
                print("G - View asset status history")
                print("I - Set depreciation rate")
                print("S - Import asset data from JSON")
                print("T - Export asset data to JSON")
                print("U - Flag low value assets")
                print("V - Change asset status")
                print("W - Add reason to last status change")
                print("X - Calculate current value")

            print("J - Search asset by name")
            print("K - Filter by category")
            print("L - Filter by status")
            print("M - Filter by value range")
            print("N - View depreciation comparison report")
            print("O - View assets per user")
            print("P - View inventory summary report")
            print("Q - View assets by user")
            print("R - Sort assets")

            print("H - Help")
            print("0 - Exit")

            choice = input("What would you like to do? ").upper().strip()

            # Create asset
            if choice == "A":
                id_choice = input("Enter asset ID: ").strip()
                name_choice = input("Enter asset name: ").strip()
                category_choice = input("Enter asset category: ").strip()
                value_choice = input("Enter asset value: ").strip()
                status_choice = input("Enter asset status: ").strip()
                assignee_choice = input("Enter asset assignee (leave blank if none: ").strip()

                if assignee_choice == "":
                    assignee_choice = None

                asset_data = {
                    "asset_id": id_choice,
                    "name": name_choice,
                    "category": category_choice,
                    "value":value_choice,
                    "status": status_choice,
                    "assigned_to": assignee_choice,
                    "history": []
                }

                self.create_new_asset(asset_data)
                self.log_crud_action("CREATE", id_choice)
                print("Asset created successfully")

            # List assets
            elif choice == "B":
                print(self.list_assets())

            # Delete asset
            elif choice == "C":
                deletion_choice = input("State the ID of the asset you wish to delete. ").strip()
                self.delete_asset(deletion_choice)
                self.log_crud_action("DELETE", deletion_choice)
                print("Asset ID: " + deletion_choice + "has been deleted")

            # Update asset field
            elif choice == "D":
                id_choice = input("State the ID of the asset you wish to update. ").strip()
                field_choice = input("State the field of the asset you wish to update. ").strip()
                new_data = input("State your change here: ").strip()
                reason = input("State your reason for change: ").strip()
                self.update_asset_field(id_choice, field_choice, new_data)
                self.record_reason_for_change(id_choice, reason)
                self.log_crud_action("UPDATE", id_choice)
                print("Asset ID: " + id_choice + "has been updated")

            # Assign asset to user
            elif choice == "E":
                id_choice = input("State the ID of the asset you wish to assign. ").strip()
                user_choice = input("State user: ").strip()
                self.assign_asset_to_user(id_choice, user_choice)
                self.log_crud_action("UPDATE", id_choice)
                print("Asset ID: " + id_choice + " has been assigned to " + user_choice)

            # Unassign asset
            elif choice == "F":
                id_choice = input("State the ID of the asset you wish to unassign. ").strip()
                self.unassign_asset(id_choice)
                self.log_crud_action("UPDATE", id_choice)
                print("Asset ID: " + id_choice + " has been unassigned from user")

            # View status history
            elif choice == "G":
                id_choice = input("State the ID of the asset history you wish to view. ").strip()
                print(self.view_status_history(id_choice))

            # Set depreciation rate
            elif choice == "I":
                rate_choice = input("State the new rate here: ").strip()
                self.set_depreciation_rate(rate_choice)

            # Search asset by name
            elif choice == "J":
                name_choice = input("State the asset name. ").strip()
                print(self.search_by_name(name_choice))

            # Filter by category
            elif choice == "K":
                category_choice = input("State the category. ").strip()
                print(self.filter_by_category(category_choice))

            # Filter by status
            elif choice == "L":
                status_choice = input("State the status. ").strip()
                print(self.filter_by_status(status_choice))

            # Filter by value
            elif choice == "M":
                min_value = float(input("State the minimum value. ").strip())
                max_value = float(input("State the maximum value. ").strip())
                print(self.filter_by_value_range(min_value, max_value))

            # View depreciation comparison report
            elif choice == "N":
                print(self.create_depreciation_comparison(list(self.assets.values())))

            # View assets per user
            elif choice == "O":
                print(self.get_assets_per_user(list(self.assets.values())))

            # View inventory summary report
            elif choice == "P":
                print(self.create_inventory_summary(list(self.assets.values())))

            #View assets by user
            elif choice == "Q":
                user_choice = input("State the user name. ").strip()
                print(self.view_assets_by_user(user_choice))

            elif choice == "R":
                sort_choice = input("State the sort choice. (Name, Value, Status, Category) ").strip().lower()
                order_choice = input("In descending order? (Y/N) ").strip().upper()
                is_descending = True if order_choice == "Y" else False
                print(self.sort_assets(sort_choice, is_descending))

            elif choice == "S":
                file_path_choice = input("State the file path. ").strip()
                print(self.import_assets_from_json(file_path_choice))

            elif choice == "T":
                file_path_choice = input("State the file path. ").strip()
                print(self.export_assets_to_json(file_path_choice))

            elif choice == "U":
                threshold_choice = input("State the threshold. ").strip()
                print(self.flag_low_value_assets(threshold_choice))

            elif choice == "V":
                asset_id = input("State the asset ID: ").strip()
                new_status = input("State new status (available/assigned/disposed): ").strip()
                print(self.change_asset_status(asset_id, new_status))

            elif choice == "W":
                asset_id = input("State the asset ID: ").strip()
                reason = input("State the reason: ").strip()
                print(self.record_reason_for_change(asset_id, reason))

            elif choice == "X":
                asset_id = input("State the asset ID: ").strip()
                years = input("State years: ").strip()
                print(self.calculate_current_value(asset_id, years))


            # Help command
            elif choice == "H":
                print(self.help_command())

            # Exit
            elif choice == "0":
                print(self.create_backup_on_exit())
                break

            else:
                print("Invalid choice, please select a valid option.")
    def config_file_support(self, config_file):

        # Default configuration
        default = {
            "data_file": "assets.json",
            "backup_file": "assets_backup.json",
            "depreciation_rate": 0.0,
            "max_backups": 5
        }

        config = default.copy()

        try:
            with open(config_file, "r") as f:
                loaded_config = json.load(f)

                # uses new values if valid
                if isinstance(loaded_config, dict):
                    for key in default:
                        if key in loaded_config:
                            config[key] = loaded_config[key]
        # Error checking
        # use defaults if error occurs
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            pass

        # Apply depreciation rate
        try:
            rate = float(config["depreciation_rate"])
            if 0 <= rate <= 1:
                self.depreciation_rate = rate
        # if error then set to default
        except Exception:
            self.depreciation_rate = default["depreciation_rate"]

        return config
    def help_command(self):
        print("\n Help: List of available commands")
        print("A: Create new asset - Create a new asset with a name, category, value and status")
        print("B: List all assets - List all current assets and their fields")
        print("C: Delete asset - Delete a specific asset")
        print("D: Update asset field - Update a specific field of an asset")
        print("E: Assign asset to user - Assign an asset to a specific user")
        print("F: Unassign asset - Unassign an asset from a specific user and becomes available")
        print("G: View asset status history - View an asset's status history")
        print("I: Set depreciation rate - Set a rate for asset values to depreciate annually")
        print("J: Search asset by name - Search for assets by their name")
        print("K: Filter by category - Filter assets by their category")
        print("L: Filter by status - Filter assets by their status")
        print("M: Filter by value range - Filter assets by a range of values")
        print("N: View depreciation comparison report - Shows a report of all assets with their change in value")
        print("O: View assets per user - Shows a list of all assets and if they are assigned to a user")
        print("P: View inventory summary report - Shows a report of all assets summarised by category and status")
        print("Q: View assets by user - Shows all assets assigned to a specific user")
        print("R: Sort assets - Sort assets by their name, value, status or category")
        print("S: Import asset data from JSON - Import asset data from a JSON file")
        print("T: Export asset data from JSON - Export asset data to a JSON file")
        print("U: Flag low value assets - Flag assets with value below a certain threshold")
        print("V: Change asset status - Status details available/assigned/disposed")
        print("W: Add reason to last status change - Manually record change for asset ID")
        print("X: Calculate current value - Calculate current value for asset")
