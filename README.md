# 🛡️ Privilege Drift Detection

This project detects **privilege drift** — any change in user access rights — by comparing the current privilege state against a previously saved **snapshot**.

It helps administrators identify when users gain, lose, or change access levels over time.

---

## 📁 Project Structure
```
.
├── data/
│ └── current_state.json # Current privileges for all users
├── snapshots/
│ ├── snapshot-2025-11-10T10-03-48.json # Automatically created snapshots
│ └── ... (more snapshots)
├── drift.py # Main Python script
└── README.md # Documentation

```
---

## ⚙️ How It Works

### 1️⃣ Current State

The file `data/current_state.json` holds the **latest privileges** for all users.  
Each user has a `privileges` list, with each entry defining one access right:

```json
[
  {
    "user": "alice",
    "privileges": [
      {"name": "admin_console", "access_level": "admin"}
    ]
  },
  {
    "user": "dave",
    "privileges": [
      {"name": "printer_queue", "access_level": "admin"},
      {"name": "vpn_access", "access_level": "admin"}
    ]
  }
]
```
2️⃣ Snapshots

When you create a snapshot, the program saves the current state into the snapshots/ directory.
Filenames are timestamped automatically (e.g., snapshot-2025-11-10T10-03-48.json).
These serve as baselines for future comparisons.
3️⃣ Drift Detection

The script compares:

    Current privileges → data/current_state.json

    Snapshot privileges → latest .json file in snapshots/

It detects three types of changes:
Type	Meaning
ADDED	A new privilege was granted to a user.
REMOVED	A privilege was revoked or no longer exists.
MODIFIED	A privilege still exists but its access level changed.
Example Output

Users with drift: dave
Findings (snapshot: snapshots/snapshot-2025-11-10T10-03-48.json)
USER        PRIVILEGE           TYPE      DETAILS
----------  ------------------  --------  ----------------
dave        printer_queue       MODIFIED  no_access → admin
dave        vpn_access          ADDED

🧠 How the Code Works
Function	Purpose
load_json() / save_json()	Reads and writes JSON safely.
create_snapshot()	Saves a timestamped copy of the current state.
latest_snapshot_path()	Finds the newest snapshot in snapshots/.
normalize_records()	Flattens user records (handles both flat and nested JSON).
detect_drift()	Compares current_state.json with the latest snapshot and reports differences.
main_menu()	Simple CLI menu to run snapshot creation or drift detection.
🖥️ Usage
▶️ Run the Script

python drift.py

🧭 Menu Options

Privilege Drift Detection
-------------------------
1) Create snapshot
2) Detect drift (latest snapshot)
Select an option (1/2):

Option 1 — Create Snapshot

Saves the current privileges from data/current_state.json into snapshots/.
Option 2 — Detect Drift

Compares the current privileges against the most recent snapshot and prints any changes.
🧩 Example Workflow

    Create initial state
    Set up data/current_state.json in the nested format shown above.

    Take a baseline

python drift.py

Choose 1 to create a snapshot.

Make changes
Edit data/current_state.json (add, remove, or modify privileges).

Detect drift

    python drift.py

    Choose 2 to compare the current file to the last snapshot.

🧰 Requirements

    Python 3.8 or newer

    Uses only built-in libraries (os, json, datetime) — no installs required

🧾 Notes

    Snapshots are plain JSON for transparency and easy version control.

    Changing a user’s "access_level" will be flagged as MODIFIED.

    You can extend this script to email reports or log results to a file.
