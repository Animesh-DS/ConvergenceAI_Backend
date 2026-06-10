import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.debate_schemas import UploadResponse
from app.services.parser_service import extract_text_from_file
from app.core.storage import read_db, write_db

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        parsed_text = await extract_text_from_file(file.filename, content)
        
        if not parsed_text:
            raise HTTPException(status_code=400, detail="Could not extract text from file.")

        problem_id = f"prob_{uuid.uuid4().hex[:8]}"
        
        # --- FIXED: Persist directly to JSON File instead of problems_db ---
        db = await read_db()
        
        # Ensure the 'problems' key exists just in case
        if "problems" not in db:
            db["problems"] = {}
            
        db["problems"][problem_id] = parsed_text
        await write_db(db)
        # -------------------------------------------------------------------
        
        return UploadResponse(
            problem_id=problem_id,
            parsed_text=parsed_text,
            status="ready"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))