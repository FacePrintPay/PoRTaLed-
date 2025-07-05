# FastAPI backend for CygNus NLP2CODE Console with Planetary Agent Routing, Webhook Endpoints, and Deployment Setup

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

# ---- Config ----
ELEVENLABS_API_KEY = "your-elevenlabs-api-key"
ELEVENLABS_VOICE_ID = "your-voice-id"

planetary_agents = {
    "Mercury": "Push2Repo",
    "Mars": "NotebookLM",
    "Saturn": "NLP2CODE",
    "Jupiter": "CoManDeck",
    "Neptune": "SLAMAR",
    "Sedna": "HeylloGen",
}

# ---- Models ----
class NLPRequest(BaseModel):
    instruction: str
    agent: str

class AvatarRequest(BaseModel):
    action: str
    agent: str

class TTSRequest(BaseModel):
    text: str
    agent: str

class WebhookPayload(BaseModel):
    event: str
    data: dict
    agent: str

# ---- Routes ----
@app.post("/api/nlp2code")
async def parse_instruction(request: NLPRequest):
    instruction = request.instruction
    agent = request.agent
    routed_service = planetary_agents.get(agent, "CygNus")
    parsed = f"[{routed_service}] {instruction.replace('Animate avatar to', '[ACTION]').strip()}"
    return {"parsed": parsed, "agent": agent, "service": routed_service}

@app.post("/api/avatar")
async def control_avatar(request: AvatarRequest):
    agent = request.agent
    action = request.action
    routed_service = planetary_agents.get(agent, "CygNus")
    print(f"Triggering avatar action via {routed_service}: {action}")
    return {"status": "Avatar action routed", "agent": agent, "service": routed_service}

@app.post("/api/tts")
async def generate_tts(request: TTSRequest):
    agent = request.agent
    routed_service = planetary_agents.get(agent, "CygNus")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": request.text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return JSONResponse(content={"status": "TTS generated", "agent": agent, "service": routed_service}, status_code=200)
    else:
        return JSONResponse(content={"error": "TTS failed", "agent": agent, "service": routed_service}, status_code=500)

@app.post("/api/webhook")
async def webhook_handler(request: WebhookPayload):
    agent = request.agent
    routed_service = planetary_agents.get(agent, "CygNus")
    event = request.event
    print(f"📡 Webhook from {routed_service} [{agent}]: {event}")
    print(f"Data: {request.data}")
    return {"status": "Webhook received", "agent": agent, "service": routed_service}

@app.get("/api/agents")
async def list_agents():
    return {"planetary_agents": planetary_agents}
