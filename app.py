from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "state.json"

app = FastAPI()

@app.get("/api/state")
def get():
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}

@app.post("/api/state")
async def put(data: dict):
    STATE_FILE.write_text(json.dumps(data))
    return {"ok": True}

app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True))
