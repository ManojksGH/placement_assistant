# backend/app.py
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

from .auth_google import router as google_router
from .data_store import save_phone, set_auto_process, scan_inbox, get_auto_process_emails

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_ORIGIN","http://localhost:5173")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(google_router, prefix="/google")

class PhoneIn(BaseModel):
    email: str
    phone: str
    auto_process: bool | None = False

@app.get("/health")
def health(): return {"ok":True}

@app.post("/user/phone")
def user_phone(inp: PhoneIn):
    save_phone(inp.email, inp.phone)
    set_auto_process(inp.email, bool(inp.auto_process))
    return {"ok":True, "auto": bool(inp.auto_process)}

@app.get("/gmail/scan")
def gmail_scan(email: str):
    items = scan_inbox(email)
    return {"items": items}

@app.post("/train")
def train_endpoint(data: dict):
    # expects {"texts": [...], "labels":[...]}
    from .model_train import train_and_save
    texts = data.get("texts",[])
    labels = data.get("labels",[])
    if not texts or not labels or len(texts)!=len(labels):
        return {"ok":False,"error":"invalid payload"}
    score, path = train_and_save(texts, labels)
    return {"ok":True,"score":score,"path":path}

@app.post("/classify")
def classify_endpoint(payload: dict):
    text = payload.get("text","")
    from .classifier import predict
    return predict(text)

@app.on_event("startup")
async def start_auto_scanner():
    async def worker():
        while True:
            emails = get_auto_process_emails()
            for e in emails:
                try:
                    scan_inbox(e)
                except Exception as exc:
                    print("[scanner] error", exc)
            await asyncio.sleep(60)
    asyncio.create_task(worker())
