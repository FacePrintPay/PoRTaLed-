from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from backend.agents import load_agent

AGENT_NAMES = ["Jupiter","Saturn","Uranus","Neptune"]
app = FastAPI(title="Giant Agents Gateway", version="1.0")

class RunRequest(BaseModel):
    payload: Dict[str, Any] = {}

@app.get("/health")
def health():
    return {"group": "giants", "agents": AGENT_NAMES, "status": "ok"}

@app.post("/agent/{name}")
def run_agent(name: str, req: RunRequest):
    if name not in AGENT_NAMES:
        raise HTTPException(status_code=404, detail=f"Unknown giant agent {name}")
    return load_agent(name)(req.payload)
