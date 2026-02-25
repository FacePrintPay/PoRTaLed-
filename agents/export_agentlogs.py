#!/usr/bin/env python3
# =========================================================
# Planetary AI Agent Log Exporter
# =========================================================

import os, json, glob, datetime, re
from collections import defaultdict

HOME = os.path.expanduser("~")
LOG_DIR = os.path.join(HOME, "logs/agents")
BUS_FILE = os.path.join(HOME, "ai_metaverse/agents_bus.json")
SUMMARY_DIR = os.path.join(HOME, "ai_metaverse/summary")
WEB_REPO = os.path.join(HOME, "ai_metaverse_web")  # adjust if your repo lives elsewhere
PUBLIC_DIR = os.path.join(WEB_REPO, "public", "agentlogs")

os.makedirs(SUMMARY_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

AGENTS = [
  "Sun","Moon","Mercury","Venus","Earth","Mars","Jupiter","Saturn","Uranus",
  "Neptune","Pluto","Ceres","Haumea","Makemake","Eris","Io","Europa",
  "Ganymede","Callisto","Titan","Chronos","Recon","CICD","ALFAI","MultiTasker","Keyholder"
]

def sanitize(line: str) -> str:
    return re.sub(r'(api[_-]?key|token|secret)[=:]\s*\S+', r'\1=[REDACTED]', line, flags=re.I).strip()

def read_tail(path, n=20):
    if not os.path.exists(path): return []
    with open(path,'r',errors='ignore') as f:
        return [sanitize(x) for x in f.readlines()[-n:]]

def build_payload():
    now = datetime.datetime.utcnow().isoformat() + "Z"
    items = []
    for agent in AGENTS:
        lf = os.path.join(LOG_DIR, f"{agent}.log")
        items.append({
            "agent": agent,
            "entries": read_tail(lf, 10),
            "has_log": os.path.exists(lf)
        })
    bus = {}
    if os.path.exists(BUS_FILE):
        try:
            with open(BUS_FILE) as b: bus = json.load(b)
        except: pass
    return {"updated_at": now, "agents": items, "bus": bus}

def write_outputs(payload):
    with open(os.path.join(PUBLIC_DIR,"data.json"),"w") as f:
        json.dump(payload, f, indent=2)

    md = [f"# Agent Logs – {payload['updated_at']}"]
    for item in payload["agents"]:
        md.append(f"## {item['agent']}")
        md.extend([f"- {line}" for line in item["entries"]]) if item["entries"] else md.append("_no log yet_")
    with open(os.path.join(PUBLIC_DIR,"summary.md"),"w") as f:
        f.write("\n".join(md))

if __name__ == "__main__":
    p = build_payload()
    write_outputs(p)
    print("✓ agentlogs exported to public/agentlogs/")
