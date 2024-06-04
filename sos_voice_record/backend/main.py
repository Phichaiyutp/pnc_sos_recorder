from datetime import datetime
from fastapi import FastAPI, HTTPException, status
from attachment_handler import AttachmentHandler
from voice_log import VoiceLogging
from contextlib import asynccontextmanager
from fastapi_utilities import repeat_at

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    task()
    yield
    # --- shutdown ---

app = FastAPI(lifespan=lifespan)

attachment_handler = AttachmentHandler()

@app.post("/check_ids")
def check_ids(sos_ids: list[int]):
    result = attachment_handler.check_id(sos_ids)
    return result

@app.post("/download_attachments")
def download_attachments(sos_ids: list[int], call_timestamps: list[datetime]):
    result = attachment_handler.download_attachments(sos_ids, call_timestamps)
    if not result['ok']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result['error'])
    return result

@app.get("/get_attachments")
def get_attachments():
    result = attachment_handler.get_attachments()
    if not result['ok']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result['error'])
    return result

@app.post("/voice_log")
def voice_logging():
    result = VoiceLogging()
    if not result['ok']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result['error'])
    return result

@app.get("/voice_log")
def get_all_voice_logs():
    result = attachment_handler.get_voice_logs()
    if not result['ok']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result['error'])
    return result

@app.get("/voice_log/{sos_id}")
def get_voice_log_by_id(sos_id: int):
    result = attachment_handler.get_voice_log(sos_id=sos_id)
    if not result['ok']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result['error'])
    return result

@app.get("/voice_log_remove")
def get_all_voice_logs():
    result = attachment_handler.get_voice_logs_garbage()
    if not result['ok']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result['error'])
    return result



@repeat_at(cron="*/1 * * * *")
def task():
    result = VoiceLogging()
    print(result)