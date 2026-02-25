#!/usr/bin/env python3
import os, json, time, sys
from datetime import datetime

AGENT_NAME = "Mercury"
TITLE = "Communications Officer"
DUTIES = "APIs, GitHub, webhooks"

BASE_DIR = os.path.expanduser("~/ai_metaverse")
BUS_FILE = os.path.join(BASE_DIR, "agents_bus.json")
LOG_FILE = os.path.join(BASE_DIR, "logs/agents", f"{AGENT_NAME}.log")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg):
    entry = f"[{datetime.now()}] {AGENT_NAME}: {msg}"
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")
    print(entry)

def load_bus():
    if os.path.exists(BUS_FILE):
        try:
            with open(BUS_FILE) as f:
                return json.load(f)
        except:
            return {"agents": {}}
    return {"agents": {}}

def communicate(status, msg):
    bus = load_bus()
    if "agents" not in bus:
        bus["agents"] = {}
    if AGENT_NAME not in bus["agents"]:
        bus["agents"][AGENT_NAME] = []
    entry = {"timestamp": datetime.now().isoformat(), "agent": AGENT_NAME, "status": status, "message": msg}
    bus["agents"][AGENT_NAME].append(entry)
    if len(bus["agents"][AGENT_NAME]) > 50:
        bus["agents"][AGENT_NAME] = bus["agents"][AGENT_NAME][-50:]
    with open(BUS_FILE, "w") as f:
        json.dump(bus, f, indent=2)

def get_pending_tasks():
    bus = load_bus()
    if AGENT_NAME not in bus.get("agents", {}):
        return []
    return [e for e in bus["agents"][AGENT_NAME] if isinstance(e, dict) and e.get("status") == "new_task"]

def execute_task(task):
    msg = task.get("message", "Unknown")
    log(f"Executing: {msg}")
    time.sleep(2)
    communicate("completed", f"Done: {msg}")

def heartbeat_loop():
    log(f"Starting mission mode - {TITLE}")
    communicate("active", f"Initialized - {DUTIES}")
    counter = 0
    try:
        while True:
            counter += 1
            if counter % 10 == 0:
                communicate("active", f"Heartbeat #{counter//10}")
                log(f"Heartbeat #{counter//10}")
            tasks = get_pending_tasks()
            if tasks:
                for task in tasks:
                    execute_task(task)
            time.sleep(6)
    except KeyboardInterrupt:
        communicate("shutdown", "Terminated")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mission":
        heartbeat_loop()
    else:
        communicate("test", f"Test - {DUTIES}")
