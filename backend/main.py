from fastapi import FastAPI
from backend.config import validate_config
from backend.config import ALLOWED_ORIGINS
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.resume import router as resume_router
from backend.routers.interview import router as interview_router

validate_config()

app = FastAPI(title="Real-Time AI Interview Simulator", version= "1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router ,prefix="/api")
app.include_router(interview_router ,prefix="/api")

@app.get("/")
def check():
    return {"status": "ok"}
