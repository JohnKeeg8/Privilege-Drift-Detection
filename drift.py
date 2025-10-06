#!/usr/bin/env python3

"""

drift.py — simple privilege drift demo

Menu:

  1) Create snapshot

  2) Detect drift (latest snapshot vs current_state.json)

"""



import os

import json

from datetime import datetime



DATA_PATH = "data/current_state.json"

SNAP_DIR = "snapshots"

RISK = {"admin": 10, "user": 5, "no_access": 1}



# ---------- Utilities ----------

def load_json(path):

    with open(path, "r", encoding="utf-8") as f:

        return json.load(f)



def save_json(path, data):

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:

        json.dump(data, f, indent=2)



def latest_snapshot_path():

    if not os.path.isdir(SNAP_DIR):

        return None

    files = [f for f in os.listdir(SNAP_DIR) if f.endswith(".json")]

    if not files:

        return None

    files.sort(reverse=True)

    return os.path.join(SNAP_DIR, files[0])



def identity(row):

    return (row.get("user"), row.get("privilege"))



def risk_score(row):

    return RISK.get(str(row.get("access_level", "")).lower(), 1)





# ---------- Core actions ----------

def create_snapshot():

    if not os.path.exists(DATA_PATH):

        print(f"[!] Current state not found at {DATA_PATH}. Create it first.")

        return

    current = load_json(DATA_PATH)

    ts = datetime.now().strftime("baseline-%Y-%m-%dT%H-%M-%S")

    out_path = os.path.join(SNAP_DIR, f"{ts}.json")

    save_json(out_path, current)

    print(f"[✓] Snapshot saved → {out_path}")



def detect_drift():

    if not os.path.exists(DATA_PATH):

        print(f"[!] Current state not found at {DATA_PATH}.")

        return

    current = load_json(DATA_PATH)



    baseline_path = latest_snapshot_path()

    if not baseline_path or not os.path.exists(baseline_path):

        print("[!] No snapshot found. Create one first (option 1).")

        return

    baseline = load_json(baseline_path)



    base_map = {identity(r): r for r in baseline}

    curr_map = {identity(r): r for r in current}



    added, removed = [], []



    # ADDED privileges (present now, absent in baseline)

    for k, cur in curr_map.items():

        if k not in base_map:

            added.append({

                "user": cur.get("user"),

                "privilege": cur.get("privilege"),

                "type": "ADDED",

                "risk": risk_score(cur)

            })



    # REMOVED privileges (present in baseline, missing now)

    for k, base in base_map.items():

        if k not in curr_map:

            removed.append({

                "user": base.get("user"),

                "privilege": base.get("privilege"),

                "type": "REMOVED",

                "risk": risk_score(base)

            })



    findings = added + removed

    findings.sort(key=lambda r: (-r["risk"], r["type"], r["user"] or "", r["privilege"] or ""))



    if not findings:

        print(f"[✓] No drift detected against baseline: {baseline_path}")

        return



    users_with_drift = sorted({f["user"] for f in findings if f.get("user")})

    print(f"Users with drift: {', '.join(users_with_drift)}")

    print(f"Findings (baseline: {baseline_path})")

    print("USER   PRIVILEGE           TYPE     RISK")

    print("-----  ------------------  -------  ----")

    for f in findings:

        user = (f["user"] or "")[:12].ljust(5)

        priv = (f["privilege"] or "")[:18].ljust(18)

        typ  = f["type"].ljust(7)

        rsk  = str(f["risk"]).rjust(4)

        print(f"{user}  {priv}  {typ}  {rsk}")





# ---------- Menu ----------

def main_menu():

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





if __name__ == "__main__":

    os.makedirs("data", exist_ok=True)

    os.makedirs(SNAP_DIR, exist_ok=True)

    main_menu()


