from asset_manager import AssetManager

def main():
    manager = AssetManager()
    print("Asset manager system")
    manager.create_new_asset({"asset_id": 1, "name": "Asset 1","category": "Asset","value": 500,"status": "Active"}) #used to create an asset

if __name__ == "__main__":
    main()