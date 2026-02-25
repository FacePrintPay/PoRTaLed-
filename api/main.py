from fastapi import FastAPI

app = FastAPI(title="Mercury Service")

@app.get("/")
def root():
    return {"status": "Mercury Agent API online"}
