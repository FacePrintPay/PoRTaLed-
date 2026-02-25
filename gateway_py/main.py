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
