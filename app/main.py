from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import debate, upload

app = FastAPI(title="Multi-Agent Debate Backend")

# Critical for P2 (Frontend) to hit this locally without CORS blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://convergenceai-frontend.vercel.app", 
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(upload.router, prefix="/api") 
app.include_router(debate.router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "Backend P1 is running and ready."}