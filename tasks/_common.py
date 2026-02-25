#!/usr/bin/env python3
from pathlib import Path
import os, json, hashlib, shutil, datetime, re, subprocess

HOME = Path(os.path.expanduser("~"))
REPORT_DIR = HOME / "ai_metaverse" / "reports"
ORGANIZED_DIR = HOME / "Organized"
DUP_DIR = ORGANIZED_DIR / "Duplicates"
EXCLUDE_DIRS = {".termux","planetary_agents","ai_metaverse","logs","Organized","Archive",".ssh","storage"}

def now(): return datetime.datetime.now().isoformat(timespec="seconds")

def ensure_dirs():
    for p in [REPORT_DIR, ORGANIZED_DIR, DUP_DIR]:
        p.mkdir(parents=True, exist_ok=True)
    for sub in ["Code","Docs","Media","Archives","Data","Config"]:
        (ORGANIZED_DIR/sub).mkdir(parents=True, exist_ok=True)

def is_excluded(p: Path) -> bool:
    try: rel = p.relative_to(HOME)
    except ValueError: return True
    return any(part in EXCLUDE_DIRS for part in rel.parts)

def walk_home():
    for p in HOME.rglob("*"):
        if p.is_file() and not is_excluded(p):
            yield p

def categorize(p: Path):
    ext = p.suffix.lower()
    code  = {".py",".js",".ts",".tsx",".jsx",".java",".kt",".go",".rs",".c",".cpp",".h",".sh"}
    conf  = {".yml",".yaml",".json",".toml",".ini",".cfg",".conf",".env"}
    docs  = {".md",".txt",".pdf",".doc",".docx",".rtf"}
    media = {".png",".jpg",".jpeg",".gif",".svg",".mp4",".mov",".webm",".mp3",".wav",".m4a"}
    arch  = {".zip",".tar",".gz",".tgz",".7z"}
    data  = {".csv",".tsv",".db",".sqlite",".parquet"}
    logs  = {".log"}
    if ext in code:  return "Code"
    if ext in conf:  return "Config"
    if ext in docs:  return "Docs"
    if ext in media: return "Media"
    if ext in arch:  return "Archives"
    if ext in data:  return "Data"
    if ext in logs:  return "Logs"
    return None

def hash_file(p: Path, chunk=1024*1024):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(chunk), b""): h.update(b)
    return h.hexdigest()

def safe_move(p: Path, dest_dir: Path):
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / p.name
    i = 1
    while dest.exists():
        dest = dest_dir / f"{p.stem}_{i}{p.suffix}"
        i += 1
    p.replace(dest)
    return dest

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f: json.dump(data, f, indent=2)

def append_report(name, data):
    path = REPORT_DIR / name
    write_json(path, data)
    print(f"[{now()}] wrote {path}")

def top_dirs_by_size(limit=20):
    sizes = {}
    for p in walk_home():
        try:
            d = str(p.parent)
            sizes[d] = sizes.get(d, 0) + p.stat().st_size
        except Exception: pass
    return sorted(([d,s] for d,s in sizes.items()), key=lambda x: x[1], reverse=True)[:limit]

def find_git_repos():
    repos=[]
    for p in HOME.rglob(".git"):
        if is_excluded(p): continue
        repo = p.parent
        remotes=[]
        try:
            out = subprocess.check_output(["/data/data/com.termux/files/usr/bin/bash","-lc", f"cd '{repo}'; git remote -v"], stderr=subprocess.STDOUT).decode()
            for line in out.strip().splitlines():
                parts=line.split()
                if len(parts)>=2: remotes.append(parts[1])
        except Exception: pass
        repos.append({"path":str(repo),"remotes":sorted(set(remotes))})
    return repos

def schedule_summary(agent_log_dir: Path):
    info=[]
    for p in agent_log_dir.glob("*_agent.sh.log"):
        try:
            last = p.read_text(errors="ignore").strip().splitlines()[-1]
        except Exception:
            last = "n/a"
        info.append({"agent": p.name, "last_line": last[-160:] if isinstance(last, str) else "n/a"})
    return info

def try_lock():
    lock = HOME / ".pathos_swarm.lock"
    try:
        fd = os.open(str(lock), os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
        os.write(fd, str(os.getpid()).encode()); os.close(fd)
        return lock
    except FileExistsError:
        print(f"[{now()}] lock busy; skipping")
        return None

def release_lock(lock):
    try: os.remove(lock)
    except Exception: pass

def organize_files(category: str, limit=200):
    moved=0
    for p in walk_home():
        if moved>=limit: break
        cat = categorize(p)
        if cat != category: continue
        # Skip if already organized
        try:
            if str(p).startswith(str(ORGANIZED_DIR)): continue
            dest = ORGANIZED_DIR / category
            safe_move(p, dest)
            moved+=1
            print(f"[{now()}] moved -> {dest}/{p.name}")
        except Exception as e:
            print(f"[{now()}] move_fail: {p} :: {e}")
    append_report(f"organize_{category.lower()}.json", {"category":category,"moved":moved,"time":now()})
