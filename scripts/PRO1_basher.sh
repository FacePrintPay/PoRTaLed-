#!/data/data/com.termux/files/usr/bin/env bash
# PRO1 Basher — Nano → Build → Run (C++ Gateway w/ Python fallback)
# Works in bash or zsh
set -Eeuo pipefail

# --- Paths ---
ROOT="${ROOT:-$HOME/aikre8tive}"
SRC_CPP="$ROOT/cpp_gateway"
THIRD="$SRC_CPP/third_party"
BUILD="$SRC_CPP/build"
LOGDIR="$ROOT/logs"
RUNDIR="$ROOT/run"
PY_GW_DIR="$ROOT/gateway_py"

mkdir -p "$THIRD" "$BUILD" "$LOGDIR" "$RUNDIR" "$PY_GW_DIR"

# --- Utilities ---
note(){ printf "\033[1;36m[NOTE]\033[0m %s\n" "$*"; }
ok(){   printf "\033[1;32m[OK]\033[0m   %s\n" "$*"; }
warn(){ printf "\033[1;33m[WARN]\033[0m %s\n" "$*"; }
err(){  printf "\033[1;31m[ERR]\033[0m  %s\n" "$*"; }

need(){
  command -v "$1" >/dev/null 2>&1 || { err "missing: $1"; return 1; }
}

pidfile(){
  case "$1" in
    cpp) echo "$RUNDIR/gateway_cpp.pid" ;;
    py)  echo "$RUNDIR/gateway_py.pid" ;;
  esac
}

kill_if_running(){
  local pf; pf="$(pidfile "$1")"
  if [[ -f "$pf" ]]; then
    local pid; pid="$(cat "$pf" || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      note "Stopping $1 gateway (pid $pid)"
      kill "$pid" 2>/dev/null || true
      sleep 0.5
      pkill -9 -P "$pid" 2>/dev/null || true
    fi
    rm -f "$pf"
  fi
}

# --- Ensure minimal C++ project (without the crow header) ---
ensure_cpp_skeleton(){
  mkdir -p "$SRC_CPP"
  # main.cpp (as provided earlier)
  if [[ ! -f "$SRC_CPP/main.cpp" ]]; then
    note "Writing C++ gateway skeleton (main.cpp)"
    cat > "$SRC_CPP/main.cpp" <<'CPP'
#include <crow_all.h>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <filesystem>
#include <future>
#include <mutex>
#include <optional>
#include <queue>
#include <string>
#include <thread>
#include <unordered_map>
#include <fstream>
#include <condition_variable>
#include <array>
using namespace std;
namespace fs = std::filesystem;

struct Job {
    string id, agent, payload, stdout_s, stderr_s, status = "queued";
    int exit_code = -1;
};
class JobStore {
    mutex m_;
    unordered_map<string, Job> jobs_;
public:
    string put(Job j){ lock_guard<mutex> lk(m_); auto id=j.id; jobs_.emplace(id, move(j)); return id; }
    optional<Job> get(const string& id){ lock_guard<mutex> lk(m_); auto it=jobs_.find(id); if(it==jobs_.end()) return nullopt; return it->second; }
    void update(const Job& j){ lock_guard<mutex> lk(m_); jobs_[j.id]=j; }
};
class Queue {
    mutex m_; condition_variable cv_; queue<string> q_;
public:
    void push(const string& id){ { lock_guard<mutex> lk(m_); q_.push(id);} cv_.notify_one(); }
    string pop(){ unique_lock<mutex> lk(m_); cv_.wait(lk,[&]{return !q_.empty();}); auto id=q_.front(); q_.pop(); return id; }
};
static string run_cmd_capture(const string& cmd, int& exit_code){
    array<char,4096> buf{}; string out; FILE* pipe=popen(cmd.c_str(),"r");
    if(!pipe){ exit_code=-1; return ""; }
    while(fgets(buf.data(), (int)buf.size(), pipe)) out+=buf.data();
    exit_code = pclose(pipe);
    return out;
}
int main(){
    const string repo_root = fs::current_path().string();
    const fs::path agents_dir = fs::path(repo_root) / "backend" / "agents";
    unordered_map<string,string> allow = {
        {"Sun","Sun.py"},{"Mercury","Mercury.py"},{"Venus","Venus.py"},{"Earth","Earth.py"},{"Mars","Mars.py"},
        {"Jupiter","Jupiter.py"},{"Saturn","Saturn.py"},{"Uranus","Uranus.py"},{"Neptune","Neptune.py"},
        {"Pluto","Pluto.py"},{"Luna","Luna.py"},{"Ceres","Ceres.py"},{"Haumea","Haumea.py"},{"Makemake","Makemake.py"},
        {"Eris","Eris.py"},{"Io","Io.py"},{"Europa","Europa.py"},{"Ganymede","Ganymede.py"},{"Callisto","Callisto.py"},
        {"Titan","Titan.py"},{"Enceladus","Enceladus.py"},{"Triton","Triton.py"},{"Charon","Charon.py"},
        {"Phobos","Phobos.py"},{"Deimos","Deimos.py"}
    };
    atomic<uint64_t> seq{1}; JobStore store; Queue queue;

    auto worker = [&]{
        for(;;){
            auto id = queue.pop();
            auto jopt = store.get(id); if(!jopt) continue; auto job=*jopt;
            auto it=allow.find(job.agent);
            if(it==allow.end()){ job.status="error"; job.stderr_s="Unknown agent"; store.update(job); continue; }
            fs::path agent_path = agents_dir / it->second;
            if(!fs::exists(agent_path)){ job.status="error"; job.stderr_s="Agent not found"; store.update(job); continue; }
            job.status="running"; store.update(job);
            fs::path tmp = fs::path(repo_root)/("tmp_payload_"+job.id+".json");
            { ofstream ofs(tmp); ofs<<job.payload; }
            string cmd = string("python3 \"")+agent_path.string()+"\" < \""+tmp.string()+"\" 2>&1";
            int code=-1;
            packaged_task<string()> task([&]{ return run_cmd_capture(cmd, code); });
            auto fut = task.get_future();
            thread(move(task)).detach();
            if(fut.wait_for(chrono::seconds(60))==future_status::timeout){
                job.status="timeout"; job.exit_code=124; job.stderr_s="agent execution timed out (60s)"; store.update(job);
            }else{
                job.stdout_s=fut.get();
                #ifdef WIFEXITED
                  job.exit_code = (WIFEXITED(code)? WEXITSTATUS(code): code);
                #else
                  job.exit_code = code;
                #endif
                job.status = (job.exit_code==0? "done":"error");
                store.update(job);
            }
            error_code ec; fs::remove(tmp, ec);
        }
    };
    thread(worker).detach(); thread(worker).detach();

    crow::SimpleApp app;
    CROW_ROUTE(app, "/health")([]{
        crow::json::wvalue j; j["ok"]=true; j["service"]="aikre8tive-gateway-cpp"; return j;
    });
    CROW_ROUTE(app, "/run/<string>").methods(crow::HTTPMethod::Post)
    ([&](const crow::request& req, crow::response& res, const string& agent){
        if(req.body.empty()){ res.code=400; res.write(R"({"error":"empty body"})"); return res.end(); }
        Job j; j.id=to_string(seq.fetch_add(1)); j.agent=agent; j.payload=req.body;
        store.put(j); queue.push(j.id);
        crow::json::wvalue out; out["job_id"]=j.id; out["agent"]=j.agent; out["status"]=j.status;
        res.code=202; res.write(crow::json::dump(out)); res.end();
    });
    CROW_ROUTE(app, "/jobs/<string>")([&](const string& id){
        auto jopt = store.get(id); if(!jopt) return crow::response(404, R"({"error":"not found"})");
        const auto& j=*jopt; crow::json::wvalue out;
        out["id"]=j.id; out["agent"]=j.agent; out["status"]=j.status; out["exit_code"]=j.exit_code;
        out["stdout"]=j.stdout_s; out["stderr"]=j.stderr_s; return crow::response{crow::json::dump(out)};
    });

    const char* port_env = getenv("PORT"); int port = port_env? atoi(port_env): 8080;
    app.port((uint16_t)port).multithreaded().run();
}
CPP
  fi

  # CMake
  if [[ ! -f "$SRC_CPP/CMakeLists.txt" ]]; then
    note "Writing CMakeLists.txt"
    cat > "$SRC_CPP/CMakeLists.txt" <<'CMAKE'
cmake_minimum_required(VERSION 3.16)
project(aikre8tive_gateway_cpp LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(gateway main.cpp)
target_include_directories(gateway PRIVATE ${CMAKE_SOURCE_DIR}/third_party)
target_link_libraries(gateway pthread)
CMAKE
  fi
}

# --- Ensure Python fallback gateway ---
ensure_python_gateway(){
  if [[ ! -f "$PY_GW_DIR/main.py" ]]; then
    note "Writing Python fallback gateway"
    cat > "$PY_GW_DIR/main.py" <<'PY'
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import subprocess, asyncio, json, os, pathlib, time
from typing import Dict

app = FastAPI(title="aikre8tive-gateway-py")
ROOT = pathlib.Path(__file__).resolve().parents[1]
AGENTS = ROOT / "backend" / "agents"
JOBS: Dict[str, dict] = {}
SEQ = 1

@app.get("/health")
def health():
    return {"ok": True, "service":"aikre8tive-gateway-py"}

@app.post("/run/{agent}")
async def run_agent(agent: str, request: Request):
    global SEQ
    body = await request.body()
    if not body:
        raise HTTPException(400, "empty body")
    job_id = str(SEQ); SEQ += 1
    JOBS[job_id] = {"status":"queued", "stdout":"", "stderr":"", "exit_code":None, "agent":agent}
    async def worker():
        try:
            path = AGENTS / f"{agent}.py"
            if not path.exists():
                JOBS[job_id].update(status="error", stderr=f"Agent not found: {path}")
                return
            proc = await asyncio.create_subprocess_shell(
                f'python3 "{path}"',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT)
            JOBS[job_id]["status"]="running"
            out, _ = await asyncio.wait_for(proc.communicate(body), timeout=60)
            JOBS[job_id]["stdout"]=out.decode("utf-8", "ignore")
            JOBS[job_id]["exit_code"]=proc.returncode
            JOBS[job_id]["status"]="done" if proc.returncode==0 else "error"
        except asyncio.TimeoutError:
            JOBS[job_id].update(status="timeout", exit_code=124, stderr="agent execution timed out (60s)")
        except Exception as e:
            JOBS[job_id].update(status="error", stderr=str(e))
    asyncio.create_task(worker())
    return {"job_id": job_id, "agent": agent, "status": "queued"}

@app.get("/jobs/{job_id}")
def jobs(job_id: str):
    j = JOBS.get(job_id)
    if not j: raise HTTPException(404, "not found")
    return {"id": job_id, **j}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8081"))
    uvicorn.run(app, host="0.0.0.0", port=port, loop="asyncio")
PY
  fi
  # simple runner
  if [[ ! -f "$PY_GW_DIR/run.sh" ]]; then
    cat > "$PY_GW_DIR/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOGDIR="$ROOT/logs"; mkdir -p "$LOGDIR"
PORT="${PORT:-8081}"
nohup python3 "$ROOT/gateway_py/main.py" >"$LOGDIR/gateway_py.out.log" 2>"$LOGDIR/gateway_py.err.log" &
echo $! > "$ROOT/run/gateway_py.pid"
echo "[OK] Python gateway on :$PORT (pid $(cat "$ROOT/run/gateway_py.pid"))"
SH
    chmod +x "$PY_GW_DIR/run.sh"
  fi
}

# --- Build C++ (if crow header exists) ---
build_cpp(){
  need cmake; need g++
  if [[ ! -f "$THIRD/crow_all.h" ]]; then
    warn "Missing $THIRD/crow_all.h (Crow header)."
    warn "Option A: place crow_all.h into $THIRD and re-run."
    warn "Option B: use Python fallback (this script will do that automatically)."
    return 1
  fi
  (cd "$SRC_CPP" && cmake -S . -B "$BUILD" >/dev/null)
  (cd "$BUILD" && cmake --build . -j >/dev/null)
  ok "C++ gateway built"
}

run_cpp(){
  kill_if_running cpp
  local bin="$BUILD/gateway"
  [[ -x "$bin" ]] || { err "gateway binary not found. Build first."; return 1; }
  PORT="${PORT:-8080}" nohup "$bin" >"$LOGDIR/gateway_cpp.out.log" 2>"$LOGDIR/gateway_cpp.err.log" &
  echo $! > "$(pidfile cpp)"
  ok "C++ gateway on :${PORT:-8080} (pid $(cat "$(pidfile cpp)"))"
}

run_py(){
  kill_if_running py
  need python3
  ensure_python_gateway
  PORT="${PORT:-8081}" bash "$PY_GW_DIR/run.sh"
}

nano_edit(){
  need nano
  local target="${1:-$SRC_CPP/main.cpp}"
  note "Opening in nano: $target"
  mkdir -p "$(dirname "$target")"
  nano "$target"
}

quick_tests(){
  note "Testing health endpoints…"
  (sleep 1; curl -s "http://127.0.0.1:${1:-8080}/health" || true; echo) | sed 's/^/[CPP] /'
  (sleep 1; curl -s "http://127.0.0.1:${2:-8081}/health" || true; echo) | sed 's/^/[PY ] /'
  note "Trigger sample Mercury run on whichever is up…"
  # try cpp first
  if curl -s "http://127.0.0.1:${1:-8080}/health" >/dev/null 2>&1; then
    jid=$(curl -s -X POST "http://127.0.0.1:${1:-8080}/run/Mercury" -H 'content-type: application/json' -d '{"ping":"pong"}' | sed -n 's/.*"job_id":"\([^"]*\)".*/\1/p')
    [[ -n "${jid:-}" ]] && sleep 1 && curl -s "http://127.0.0.1:${1:-8080}/jobs/$jid" | sed 's/^/[CPP] /'
    echo
  elif curl -s "http://127.0.0.1:${2:-8081}/health" >/dev/null 2>&1; then
    jid=$(curl -s -X POST "http://127.0.0.1:${2:-8081}/run/Mercury" -H 'content-type: application/json' -d '{"ping":"pong"}' | sed -n 's/.*"job_id":"\([^"]*\)".*/\1/p')
    [[ -n "${jid:-}" ]] && sleep 1 && curl -s "http://127.0.0.1:${2:-8081}/jobs/$jid" | sed 's/^/[PY ] /'
    echo
  else
    warn "No gateway is listening yet."
  fi
}

usage(){
cat <<USAGE
PRO1 Basher — edit, build, and run gateways

Commands:
  --edit-cpp [file]   Open main.cpp (or file) in nano
  --build-cpp         Build the C++ gateway (requires third_party/crow_all.h)
  --run-cpp           Run the C++ gateway on \$PORT (default 8080)
  --run-py            Run the Python fallback gateway on \$PORT (default 8081)
  --all               Try C++ (build+run); if header missing, run Python
  --stop              Stop any running gateways
  --test              Hit /health and submit a sample Mercury job

Examples:
  bash scripts/PRO1_basher.sh --edit-cpp
  PORT=8080 bash scripts/PRO1_basher.sh --all
  bash scripts/PRO1_basher.sh --test
USAGE
}

# --- Main dispatch ---
cmd="${1:-}"
case "$cmd" in
  --edit-cpp)
    ensure_cpp_skeleton
    nano_edit "${2:-$SRC_CPP/main.cpp}"
    ;;
  --build-cpp)
    ensure_cpp_skeleton
    build_cpp || exit 1
    ;;
  --run-cpp)
    run_cpp || exit 1
    ;;
  --run-py)
    run_py || exit 1
    ;;
  --all)
    ensure_cpp_skeleton
    if build_cpp; then
      run_cpp
    else
      warn "Falling back to Python gateway…"
      run_py
    fi
    ;;
  --stop)
    kill_if_running cpp
    kill_if_running py
    ok "All gateways stopped."
    ;;
  --test)
    quick_tests "8080" "8081"
    ;;
  ""|--help|-h)
    usage
    ;;
  *)
    err "unknown command: $cmd"
    usage; exit 1
    ;;
esac
