# 🛡️ Privilege Drift Detection

This project detects **privilege drift** — any change in user access rights — by comparing the current privilege state against a previously saved **snapshot**.

It’s designed to help administrators monitor when users gain, lose, or change access levels over time.

---

## 📂 Project Structure

.
├── data/
│ └── current_state.json # Current privileges for all users
├── snapshots/
│ ├── snapshot-2025-11-10T10-03-48.json # Automatically created snapshots
│ └── ... more snapshots ...
├── drift.py # Main Python script
└── README.md # This documentation file


---

## ⚙️ How It Works

### 1. Current State
- `data/current_state.json` holds the **latest privileges** for all users.
- Each user has a `privileges` list, with each entry defining one access right.

Example:
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

2. Snapshots

    When you create a snapshot, the program saves the current state into the snapshots/ directory.

    Filenames are timestamped automatically (e.g., snapshot-2025-11-10T10-03-48.json).

    These serve as baselines for future comparisons.

3. Drift Detection

The script compares:

    The current privileges (data/current_state.json)

    Against the latest snapshot in snapshots/

It identifies three types of changes:
Type	Meaning
ADDED	A new privilege was granted to a user
REMOVED	A privilege was revoked or no longer exists
MODIFIED	A privilege still exists, but its access level changed (e.g., user → admin)

Example output:

Users with drift: dave
Findings (snapshot: snapshots/snapshot-2025-11-10T10-03-48.json)
USER        PRIVILEGE           TYPE      DETAILS
----------  ------------------  --------  ----------------
dave        printer_queue       MODIFIED  no_access → admin
dave        vpn_access          ADDED

🧠 How the Code Works (Overview)

    load_json() / save_json()

        Handles reading and writing JSON files safely.

    create_snapshot()

        Takes the current privileges from data/current_state.json.

        Saves them to a new timestamped snapshot file under snapshots/.

    latest_snapshot_path()

        Finds and returns the path of the most recent .json snapshot.

    normalize_records()

        Flattens user records so the drift detection logic can treat both:

            Flat records ({"user": "x", "privilege": "y", ...})

            Nested records ({"user": "x", "privileges": [ ... ]})
            the same way.

    detect_drift()

        Compares the current and snapshot privilege maps.

        Builds a list of changes:

            Added privileges (in current but not snapshot)

            Removed privileges (in snapshot but not current)

            Modified privileges (same privilege, different access level)

    main_menu()

        Provides a simple terminal menu to create snapshots or detect drift.

🖥️ Usage
1️⃣ Run the script

From your terminal:

python drift.py

2️⃣ Menu Options

Privilege Drift Detection
-------------------------
1) Create snapshot
2) Detect drift (latest snapshot)
Select an option (1/2):

Option 1 → Create snapshot

    Saves the current privileges from data/current_state.json into snapshots/.

Option 2 → Detect drift

    Compares the current privileges against the latest snapshot.

    Prints a report showing any differences.

🧩 Example Workflow

    Initial Setup

        Create your data/current_state.json using the nested structure shown above.

    Take a baseline

python drift.py

Select 1 to create a snapshot.

Make a change

    Edit data/current_state.json (add/remove/modify privileges).

Detect drift

    python drift.py

    Select 2 to compare the updated file against the latest snapshot.

🧰 Requirements

    Python 3.8+

    No external libraries required (uses only os, json, and datetime)

🧾 Notes

    Snapshots are stored in plain JSON for transparency and version control.

    The comparison is field-sensitive — changing a user’s "access_level" will trigger a MODIFIED alert.

    You can extend the code to email reports or write findings to a log file.