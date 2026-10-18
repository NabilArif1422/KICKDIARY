from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import settings
from app.database import engine, Base
from app.routers import auth_router, match_router, story_router

# Inisialisasi tabel database saat aplikasi dimulai
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API resmi KICKDIARY - Football Storytelling AI Platform (Mata Kuliah IPPL)"
)

# CORS Middleware agar dapat diakses dari browser mana pun tanpa kendala
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrasi Router
app.include_router(auth_router.router)
app.include_router(match_router.router)
app.include_router(story_router.router)

# Endpoint Healthcheck
@app.get("/api/health")
def healthcheck():
    return {
        "status": "healthy",
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected"
    }

# Siapkan folder static untuk UI web jika belum ada
static_dir = os.path.join(os.path.dirname(__file__), "app", "static")
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "KickDiary API is running! Kunjungi /docs untuk melihat dokumentasi Swagger interaktif."
    }
