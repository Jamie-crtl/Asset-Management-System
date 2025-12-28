from asset_manager import AssetManager

def main():
    manager = AssetManager()
    print("Asset manager system")
    print(f"Loaded {len(manager.assets)} assets on startup") # user story 9
    manager.create_new_asset({
        "asset_id": "5",
        "name": "Asset 3",
        "category": "property",
        "value": 500,
        "status": "available",
        "assigned_to": None,
        "history": []
    }) #used to create an asset
    print("saved assets:",len(manager.assets))

if __name__ == "__main__":
    main()