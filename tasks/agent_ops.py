#!/usr/bin/env python3
from pathlib import Path
import os, json, gzip, shutil, time, re, datetime
from _common import *

def sun():
    ensure_dirs()
    total = sum(1 for _ in walk_home())
    disk = shutil.disk_usage(str(HOME))
    report = {
        "time": now(),
        "files_scanned": total,
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_free": disk.free,
        "top_dirs": [{"dir": d, "bytes": s} for d,s in top_dirs_by_size(20)]
    }
    append_report("system_overview.json", report)

def moon():
    ensure_dirs()
    boot = HOME/".termux"/"boot"/"start_agents.sh"
    ok = boot.exists() and os.access(boot, os.X_OK)
    append_report("moon_ops.json", {"time":now(),"boot_exists":boot.exists(),"boot_executable":ok})

def mercury():
    import urllib.request
    ensure_dirs()
    status={}
    for url in ["https://1.1.1.1","https://www.google.com","https://httpbin.org/ip"]:
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                status[url]=r.status
        except Exception as e:
            status[url]=f"ERR:{e}"
    append_report("network_status.json", {"time":now(),"checks":status})

def venus():
    ensure_dirs()
    index=[]
    for p in walk_home():
        if p.suffix.lower() in {".html",".htm",".md"}:
            title=None
            try:
                txt=p.read_text(errors="ignore")
                m=re.search(r"<title>(.*?)</title>", txt, re.I|re.S) or re.search(r"^#\s+(.*)", txt, re.M)
                title=m.group(1).strip() if m else p.name
            except Exception:
                title=p.name
            index.append({"path":str(p), "title":title})
    append_report("content_index.json", {"time":now(),"count":len(index),"items":index[:500]})

def earth():
    ensure_dirs()
    stats={"files":0,"code":0,"docs":0,"config":0}
    for p in walk_home():
        stats["files"]+=1
        c = categorize(p) or "other"
        stats[c.lower()] = stats.get(c.lower(),0)+1
    append_report("knowledge_inventory.json", {"time":now(), **stats})

def mars():
    ensure_dirs()
    lock = try_lock()
    if not lock: return
    try: organize_files("Code", limit=400)
    finally: release_lock(lock)

def jupiter():
    ensure_dirs()
    append_report("strategy_top_dirs.json", {"time":now(),"top": [{"dir":d,"bytes":s} for d,s in top_dirs_by_size(30)]})

def saturn():
    ensure_dirs()
    findings=[]
    patterns=[r"AKIA[0-9A-Z]{16}", r"secret", r"api[_-]?key", r"Bearer\s+[A-Za-z0-9\._\-]+", r"-----BEGIN\s+PRIVATE\s+KEY-----"]
    for p in walk_home():
        if p.suffix.lower() in {".env",".json",".yaml",".yml",".cfg",".conf",".py",".js",".ts"}:
            try:
                txt=p.read_text(errors="ignore")
                hits=[pat for pat in patterns if re.search(pat, txt)]
                if hits: findings.append({"path":str(p),"hits":hits})
            except Exception: pass
    append_report("security_findings.json", {"time":now(),"count":len(findings),"items":findings[:500]})

def uranus():
    ensure_dirs()
    todos=[]
    for p in walk_home():
        if p.suffix.lower() in {".py",".js",".ts",".md",".txt",".sh"}:
            try:
                for ln, line in enumerate(p.read_text(errors="ignore").splitlines(),1):
                    if "TODO" in line or "FIXME" in line:
                        todos.append({"path":str(p),"line":ln,"text":line.strip()[:160]})
            except Exception: pass
    append_report("innovation_todos.json", {"time":now(),"count":len(todos),"items":todos[:1000]})

def neptune():
    ensure_dirs()
    sizes={}
    for p in walk_home():
        cat = categorize(p) or "Other"
        sizes[cat]=sizes.get(cat,0)+p.stat().st_size
    append_report("finance_sizes.json", {"time":now(),"sizes_bytes":sizes})

def pluto():
    ensure_dirs()
    risky=[]
    for p in walk_home():
        name=p.name.lower()
        if any(k in name for k in ["password","secret","creds","backup","key"]):
            risky.append(str(p))
        try:
            if (p.stat().st_mode & 0o002): # world-writable
                risky.append(str(p)+" (world-writable)")
        except Exception: pass
    append_report("risk_edge_cases.json", {"time":now(),"count":len(risky),"items":risky[:1000]})

def ceres():
    ensure_dirs()
    lock = try_lock()
    if not lock: return
    moved=0
    try:
        for p in walk_home():
            if moved>=400: break
            if categorize(p)=="Data" and not str(p).startswith(str(ORGANIZED_DIR)):
                safe_move(p, ORGANIZED_DIR/"Data"); moved+=1
    finally:
        release_lock(lock)
    append_report("data_moves.json", {"time":now(),"moved":moved})

def haumea():
    ensure_dirs()
    lock = try_lock()
    if not lock: return
    moved=0
    try:
        for p in walk_home():
            if moved>=400: break
            if p.suffix.lower() in {".png",".jpg",".jpeg",".gif",".svg"} and not str(p).startswith(str(ORGANIZED_DIR)):
                safe_move(p, ORGANIZED_DIR/"Media"); moved+=1
    finally:
        release_lock(lock)
    append_report("design_media_moves.json", {"time":now(),"moved":moved})

def makemake():
    ensure_dirs()
    lock = try_lock()
    if not lock: return
    moved=0
    try:
        for p in walk_home():
            if moved>=300: break
            if p.suffix.lower() in {".mp4",".mov",".webm",".mp3",".wav",".m4a"} and not str(p).startswith(str(ORGANIZED_DIR)):
                safe_move(p, ORGANIZED_DIR/"Media"); moved+=1
    finally:
        release_lock(lock)
    append_report("creative_media_moves.json", {"time":now(),"moved":moved})

def eris():
    ensure_dirs()
    repos=find_git_repos()
    missing=[]
    for r in repos:
        lic = Path(r["path"])/"LICENSE"
        gi  = Path(r["path"])/".gitignore"
        miss = []
        if not lic.exists(): miss.append("LICENSE")
        if not gi.exists():  miss.append(".gitignore")
        if miss: missing.append({"repo":r["path"],"missing":miss,"remotes":r["remotes"]})
    append_report("governance_repos.json", {"time":now(),"repos":repos,"missing":missing})

def io():
    ensure_dirs()
    needed=[ORGANIZED_DIR/sub for sub in ["Code","Docs","Media","Archives","Data","Config","Duplicates"]]
    created=[]
    for d in needed:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created.append(str(d))
    append_report("infra_dirs.json", {"time":now(),"created":created})

def europa():
    ensure_dirs()
    nb=[]
    for p in walk_home():
        if p.suffix.lower()==".ipynb":
            nb.append(str(p))
    append_report("research_notebooks.json", {"time":now(),"count":len(nb),"paths":nb[:1000]})

def ganymede():
    ensure_dirs()
    lock = try_lock()
    if not lock: return
    seen={},{}
    seen_hash={}
    dups=[]
    try:
        for p in walk_home():
            try:
                h=hash_file(p)
                if h in seen_hash:
                    dest = safe_move(p, DUP_DIR)
                    dups.append({"src":str(p),"moved_to":str(dest),"hash":h})
                else:
                    seen_hash[h]=str(p)
            except Exception: pass
    finally:
        release_lock(lock)
    append_report("storage_duplicates.json", {"time":now(),"duplicates":dups[:1000]})

def callisto():
    ensure_dirs()
    # perms check for executables
    boot = HOME/".termux"/"boot"/"start_agents.sh"
    fixed=[]
    if boot.exists() and not os.access(boot, os.X_OK):
        os.chmod(boot, 0o755); fixed.append(str(boot))
    for p in (HOME/"planetary_agents").glob("*_agent.sh"):
        if p.exists() and not os.access(p, os.X_OK):
            os.chmod(p, 0o755); fixed.append(str(p))
    append_report("stability_fixes.json", {"time":now(),"fixed":fixed})

def titan():
    ensure_dirs()
    # compress large .log > 5MB into Archives
    archived=[]
    for p in walk_home():
        try:
            if p.suffix.lower()==".log" and p.stat().st_size > 5*1024*1024:
                dest = ORGANIZED_DIR/"Archives"/(p.stem + ".log.gz")
                with p.open("rb") as src, gzip.open(dest, "wb") as dst: shutil.copyfileobj(src,dst)
                p.unlink()
                archived.append({"src":str(p),"dst":str(dest)})
        except Exception: pass
    append_report("archival_logs.json", {"time":now(),"archived":archived})

def chronos():
    ensure_dirs()
    agent_logs = HOME/"planetary_agents"
    summ = schedule_summary(agent_logs)
    append_report("schedule_summary.json", {"time":now(),"agents":summ})

def recon():
    ensure_dirs()
    repos = find_git_repos()
    manifests=[]
    for r in repos:
        path = Path(r["path"])
        files = [f for f in ["package.json","pyproject.toml","requirements.txt","Dockerfile","vercel.json"]
                 if (path/f).exists()]
        manifests.append({"repo":r["path"],"manifests":files,"remotes":r["remotes"]})
    append_report("recon_repos.json", {"time":now(),"repos":manifests})

def cicd():
    ensure_dirs()
    auto = os.environ.get("PATHOS_AUTO_COMMIT","0")=="1"
    ops=[]
    for r in find_git_repos():
        path = r["path"]
        try:
            if auto:
                os.system(f"/data/data/com.termux/files/usr/bin/bash -lc \"cd '{path}'; git add -A; git commit -m 'agent: auto-commit {now()}' || true\"")
                ops.append({"repo":path,"committed":True})
            else:
                status=os.popen(f"/data/data/com.termux/files/usr/bin/bash -lc \"cd '{path}'; git status --short\"").read()
                if status.strip():
                    ops.append({"repo":path,"pending_changes":status.strip().splitlines()[:50]})
        except Exception: pass
    append_report("cicd_ops.json", {"time":now(),"auto_commit":auto,"repos":ops})

def alfai():
    ensure_dirs()
    # license & policy surface
    policies=[]
    for p in walk_home():
        if p.name.lower() in {"license","license.md","privacy.md","terms.md","security.md"}:
            policies.append(str(p))
    append_report("legal_policies.json", {"time":now(),"policies":policies[:1000]})

def multitasker():
    ensure_dirs()
    # Compose dashboard from key reports
    dashboard = {
        "time": now(),
        "overview": json.loads((REPORT_DIR/"system_overview.json").read_text()) if (REPORT_DIR/"system_overview.json").exists() else {},
        "sizes":   json.loads((REPORT_DIR/"finance_sizes.json").read_text()) if (REPORT_DIR/"finance_sizes.json").exists() else {},
        "security":json.loads((REPORT_DIR/"security_findings.json").read_text()) if (REPORT_DIR/"security_findings.json").exists() else {},
        "repos":   json.loads((REPORT_DIR/"recon_repos.json").read_text()) if (REPORT_DIR/"recon_repos.json").exists() else {},
    }
    (REPORT_DIR/"dashboard.md").write_text(
        f"# PaTHos Swarm Dashboard\n\n- Time: {dashboard.get('time')}\n"
        f"- Files scanned: {dashboard.get('overview',{}).get('files_scanned')}\n"
        f"- Disk free: {dashboard.get('overview',{}).get('disk_free')}\n"
        f"- Repos tracked: {len(dashboard.get('repos',{}).get('repos',[])) if dashboard.get('repos') else 0}\n"
    )
    append_report("dashboard.json", dashboard)

ROUTER = {
 "Sun": sun, "Moon": moon, "Mercury": mercury, "Venus": venus, "Earth": earth,
 "Mars": mars, "Jupiter": jupiter, "Saturn": saturn, "Uranus": uranus, "Neptune": neptune,
 "Pluto": pluto, "Ceres": ceres, "Haumea": haumea, "Makemake": makemake, "Eris": eris,
 "Io": io, "Europa": europa, "Ganymede": ganymede, "Callisto": callisto, "Titan": titan,
 "Chronos": chronos, "Recon": recon, "CICD": cicd, "ALFAI": alfai, "MultiTasker": multitasker
}

def run(name: str):
    fn = ROUTER.get(name)
    if not fn:
        print(f"[{now()}] unknown agent {name}")
        return
    fn()

if __name__=="__main__":
    name=os.environ.get("AGENT_NAME","")
    if name: run(name)
