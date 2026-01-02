# Asset Management System - README (Run & Test guide)

- Public GitHub link: https://github.com/Jamie-crtl/Asset-Management-System

# 1 Requirements: 
Python: 3.10+ (3.11 is fine)
Testing framework and Coverage tools: pytest , coverage

# 2 Uncompress the project (.zip): 
- Copy Asset-Management-System project zip onto lab PC 
- Right click > Extract all
- Locate source code project folder: Asset-Management-System
- Inside it, you should see files such as main.py, asset.py, asset_manager.py, storage.py, All tests/, README.md

# 3 Import into PyCharm
- Open PyCharm
- Select Open
- Browse to the extracted folder: Asset-Management-System
- Click OK/Open as project
- If prompted choose Trust project

# 4 Run / Compile the Application
- In project tree, open and right click main.py > Run 'Main'
- The program output will appear in the Run console

# 5 Running All Test Cases
- All test cases are contained in: All tests/
- Folder includes Black-box tests, White-box tests (including symbolic/concolic where applicable)
- Right-click any *.py test file (e.g., *_random.py, *_symbolic.py)
- Click run to see test cases pass, to view coverage click more Run/Debug 'Run 'Python tests in ....' with Coverage'