from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import sys
from pathlib import Path

app = FastAPI()

# Path to your AI-Youtube-Shorts-Generator project
AI_PATH = Path("../AI-Youtube-Shorts-Generator-main").resolve()

sys.path.append(str(AI_PATH))

from shorts_generator.pipeline import generate_shorts


# Allow the Next.js frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ai-shorts-studio-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Folder for uploaded videos
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "AI Shorts Studio Backend Running 🚀"
    }


# ============================================================
# 1. UPLOAD LOCAL VIDEO
# ============================================================

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = generate_shorts(
            youtube_url=file_path,
            mode="local",
            num_clips=3,
            aspect_ratio="9:16",
        )

        return {
            "success": True,
            "result": result,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# ============================================================
# 2. ANALYZE YOUTUBE URL
# ============================================================

@app.post("/analyze-url")
async def analyze_url(data: dict):

    url = data.get("url")

    if not url:
        return {
            "success": False,
            "error": "YouTube URL is required."
        }

    try:
        print(f"[youtube] analyzing: {url}", flush=True)

        result = generate_shorts(
            youtube_url=url,
            mode="local",
            num_clips=3,
            aspect_ratio="9:16",
        )

        return {
            "success": True,
            "result": result,
        }

    except Exception as e:
        print(f"[youtube] ERROR: {e}", flush=True)

        return {
            "success": False,
            "error": str(e),
        }