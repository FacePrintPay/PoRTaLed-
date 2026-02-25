from fastapi import FastAPI
from routes import court

app = FastAPI(title="VideoCourts – LEGyC Law Scaffold")

app.include_router(court.router)

@app.get("/")
def root():
    return {"message": "VideoCourts LEGyC Scaffold active"}
