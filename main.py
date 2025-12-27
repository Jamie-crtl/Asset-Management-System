from asset_manager import AssetManager

def main():
    manager = AssetManager()
    print("Asset manager system")
    manager.create_new_asset({
        "asset_id": "1",
        "name": "Asset 1",
        "category": "property",
        "value": 500,
        "status": "available",
        "assigned_to": None,
        "history": []
    }) #used to create an asset

if __name__ == "__main__":
    main()