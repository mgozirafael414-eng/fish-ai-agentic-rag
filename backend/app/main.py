from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.fish_prediction import router as fish_prediction_router

# ==========================================
# CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="FishAI Agentic RAG API",
    description="Backend API for FishAI intelligent assistant",
    version="1.0.0",
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(fish_prediction_router)


# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/")
async def root():
    return {
        "success": True,
        "message": "FishAI Agentic RAG API is running",
        "version": "1.0.0",
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
async def health_check():
    return {
        "success": True,
        "status": "healthy",
        "service": "FishAI Backend",
    }
