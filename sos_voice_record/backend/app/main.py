from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; you can specify a list of origins instead
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

attachment_handler = AttachmentHandler()

@app.post("/check_ids")
def check_ids(sos_ids: list[int]):
    result = attachment_handler.check_id(sos_ids)
    return result

@app.post("/download_attachments")
def download_attachments(sos_ids: list[int], call_timestamps: list[datetime]):
    result = attachment_handler.download_attachments(sos_ids, call_timestamps)
    if not result['ok']:
        return JSONResponse(status_code=404, content=result)
    else:
        return result

@app.get("/get_attachments")
def get_attachments():
    result = attachment_handler.get_attachments()
    if not result['ok']:
        return JSONResponse(status_code=404, content=result)
    else:
        return result

@app.post("/voice_log")
def voice_logging():
    result = VoiceLogging()
    if not result['ok']:
        return JSONResponse(status_code=404, content=result)
    else:
        return result

@app.get("/voice_log")
def get_all_voice_logs():
    result = attachment_handler.get_voice_logs()
    if not result['ok']:
        return JSONResponse(status_code=404, content=result)
    else:
        return result

@app.get("/voice_log/{sos_id}")
def get_voice_log_by_id(sos_id: int):
    result = attachment_handler.get_voice_log(sos_id=sos_id)
    if not result['ok']:
        return JSONResponse(status_code=404, content=result)
    else:
        return result

@app.get("/voice_log_remove")
def get_all_voice_logs():
    result = attachment_handler.get_voice_logs_garbage()
    if not result['ok']:
        return JSONResponse(status_code=404, content=result)
    else:
        return result



@repeat_at(cron="*/1 * * * *")
def task():
    result = VoiceLogging()
    print(result)