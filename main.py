from asset_manager import AssetManager

def main():
    manager = AssetManager()
    print("--Asset Management System--")
    print(f"Statistics: Loaded {len(manager.assets)} saved assets on startup") # user story 9
    #manager.create_new_asset({
    #    "asset_id": "5",
    #    "name": "Asset 3",
    #    "category": "property",
    #    "value": 500,
    #    "status": "available",
    #    "assigned_to": None,
    #    "history": []
    #}) #used to create an asset
    #print("saved assets:",len(manager.assets))

    role = input("Enter role (admin/user): ").strip().lower()
    manager.run_text_menu(role)

if __name__ == "__main__":
    main()