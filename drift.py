import os
import json
from datetime import datetime

DATA_PATH = "data/current_state.json"
SNAP_DIR = "snapshots"


def load_json(path):  # John
    """Loads and returns the JSON data from the specified file path."""
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):  # Michael
    """Saves the given data as a JSON file at the specified path."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def latest_snapshot_path():  # John
    """Returns the path to the latest snapshot file, or None if no snapshots exist."""
    if not os.path.isdir(SNAP_DIR):
        return None
    files = sorted(
        [f for f in os.listdir(SNAP_DIR) if f.endswith(".json")],
        reverse=True,
    )
    return os.path.join(SNAP_DIR, files[0]) if files else None


def create_snapshot():  # Michael
    """Creates a snapshot of the current state and saves it with a timestamped filename."""

    if not os.path.exists(DATA_PATH):
        print(f"[!] Current state not found at {DATA_PATH}")
        return

    current = load_json(DATA_PATH)  # load current state
    ts = datetime.now().strftime("snapshot-%Y-%m-%dT%H-%M-%S")  # timestamp filename
    out_path = os.path.join(SNAP_DIR, f"{ts}.json")  # output path
    save_json(out_path, current)  # save snapshot
    print(f"[✓] Snapshot saved → {out_path}")


def normalize_records(records):
    """
    NEW (commented): takes a list of records that might be in two shapes:
      1) flat: {"user": "dave", "privilege": "printer_queue", "access_level": "admin"}
      2) nested: {"user": "dave", "privileges": [ {"name": "...", "access_level": "..."}, ... ]}
    and returns a FLAT list of dicts so the rest of the drift logic can stay simple.
    """
    flat = []
    for r in records:
        user = r.get("user")
        # case 1: already flat
        if "privilege" in r:
            flat.append({
                "user": user,
                "privilege": r.get("privilege"),
                "access_level": r.get("access_level"),
            })
        # case 2: nested privileges list
        elif "privileges" in r and isinstance(r["privileges"], list):
            for p in r["privileges"]:
                flat.append({
                    "user": user,
                    # nested one used "name" in your example
                    "privilege": p.get("name"),
                    "access_level": p.get("access_level"),
                })
        # else: ignore malformed rows silently
    return flat


def detect_drift():
    """Detects and reports privilege drift between the current state and the latest snapshot."""

    if not os.path.exists(DATA_PATH):  # checks if the current state file exists
        print(f"[!] Current state not found at {DATA_PATH}")
        return

    snapshot_path = latest_snapshot_path()  # get latest snapshot

    if not snapshot_path:  # no snapshot found
        print("[!] No snapshot found. Create one first (option 1)")
        return

    # current = now, snapshot = saved
    current_raw = load_json(DATA_PATH)          # could be flat or nested
    snapshot_raw = load_json(snapshot_path)     # could be flat or nested

    # NEW: normalize both sides so they look the same to the rest of the code
    current = normalize_records(current_raw)
    snapshot = normalize_records(snapshot_raw)

    # key = (user, privilege)
    curr_map = {(r.get("user"), r.get("privilege")): r for r in current}   # map current records in dict
    snap_map = {(r.get("user"), r.get("privilege")): r for r in snapshot}  # map snapshot records in dict

    findings = []  # list of drift findings

    # 1) ADDED — tells us if a new privilege was added (in current but not in snapshot)
    for k, cur in curr_map.items():
        if k not in snap_map:
            findings.append({
                "user": cur.get("user"),
                "privilege": cur.get("privilege"),
                "type": "ADDED",
            })

    # 2) REMOVED + MODIFIED -- tells us if a privilege was removed or changed
    for k, snap in snap_map.items():  # iterate through the snapshot records
        if k not in curr_map:  # privilege was removed
            findings.append({  # record removal
                "user": snap.get("user"),
                "privilege": snap.get("privilege"),
                "type": "REMOVED",
            })
        else:  # privilege exists, check for modifications
            cur = curr_map[k]  # get current record
            # compare access levels between snapshot and current
            if snap.get("access_level") != cur.get("access_level"):  # check for changes
                findings.append({  # record modification
                    "user": cur.get("user"),
                    "privilege": cur.get("privilege"),
                    "type": "MODIFIED",
                    "from": snap.get("access_level"),
                    "to": cur.get("access_level"),
                })

    if not findings:  # no drift found
        print(f"[✓] No drift detected against snapshot: {snapshot_path}")
        return

    # Display findings
    findings.sort(key=lambda r: (r["type"], r.get("user") or "", r.get("privilege") or ""))

    users = sorted({f["user"] for f in findings if f.get("user")})
    print(f"Users with drift: {', '.join(users)}")
    print(f"Findings (snapshot: {snapshot_path})")
    print("USER        PRIVILEGE           TYPE      DETAILS")
    print("----------  ------------------  --------  ----------------")

    for f in findings:
        user = (f["user"] or "").ljust(10)
        priv = (f["privilege"] or "").ljust(18)
        typ = f["type"].ljust(8)
        if f["type"] == "MODIFIED":
            details = f'{f.get("from")} → {f.get("to")}'
        else:
            details = ""
        print(f"{user}  {priv}  {typ}  {details}")


def main_menu():  # Michael
    print("\nPrivilege Drift Detection")
    print("-------------------------")
    print("1) Create snapshot")
    print("2) Detect drift (latest snapshot)")
    choice = input("Select an option (1/2): ").strip()

    if choice == "1":
        create_snapshot()
    elif choice == "2":
        detect_drift()
    else:
        print("[!] Invalid selection. Please run again and choose 1 or 2.")


if __name__ == "__main__":  # John
    os.makedirs("data", exist_ok=True)
    os.makedirs(SNAP_DIR, exist_ok=True)
    main_menu()
