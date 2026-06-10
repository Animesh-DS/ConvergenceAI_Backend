import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.debate_schemas import (
    StartDebateRequest, 
    StartDebateResponse, 
    DebateResultResponse
)
from app.services.debate_engine import generate_debate_stream
from app.core.storage import read_db, write_db

router = APIRouter()

@router.post("/start-debate", response_model=StartDebateResponse)
async def start_debate(request: StartDebateRequest):
    debate_id = f"deb_{uuid.uuid4().hex[:8]}"
    
    db = await read_db()
    
    # 1. Ensure the problem actually exists before starting
    if request.problem_id not in db["problems"]:
        raise HTTPException(status_code=404, detail="Problem ID not found. Upload a file first.")
    
    # 2. Persist the configuration to disk (No in-memory dicts!)
    db["debates"][debate_id] = {
        "problem_id": request.problem_id,
        "rounds": request.rounds,
        "status": "started"
    }
    db["transcripts"][debate_id] = []
    
    await write_db(db)
    
    return StartDebateResponse(debate_id=debate_id, status="started")

@router.get("/stream-debate/{debate_id}")
async def stream_debate(debate_id: str):
    db = await read_db()
    
    # 1. Fetch the exact configuration from disk
    debate_config = db["debates"].get(debate_id)
    if not debate_config:
        raise HTTPException(status_code=404, detail="Debate not found.")
        
    problem_id = debate_config["problem_id"]
    rounds = debate_config["rounds"]
    
    # 2. Pass the real dynamic variables (Removed the hardcoded "mock_prob" and rounds=2)
    generator = generate_debate_stream(debate_id, problem_id, rounds)
    
    # 3. Stream with your custom Anti-Buffering headers
    return StreamingResponse(
        generator, 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no" # Prevents Nginx/Proxies from buffering the stream
        }
    )

@router.get("/result/{debate_id}", response_model=DebateResultResponse)
async def get_result(debate_id: str):
    db = await read_db()
    
    if debate_id not in db["transcripts"]:
        raise HTTPException(status_code=404, detail="Debate not found")
        
    # Check if the final result has been generated yet
    final_result = db["debates"].get(debate_id, {}).get("final_result")
    
    return DebateResultResponse(
        debate_id=debate_id,
        status="completed" if final_result else "started",
        transcript=db["transcripts"].get(debate_id, []),
        final_result=final_result
    )