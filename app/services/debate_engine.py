import uuid
import json
from datetime import datetime
from app.schemas.debate_schemas import DebateTurnData, DebateEndData
from app.services.llm_service import generate_agent_turn, generate_final_verdict
from app.core.storage import read_db, write_db

async def generate_debate_stream(debate_id: str, problem_id: str, rounds: int):
    """Orchestrates live Groq calls, yields SSE payloads, and saves to disk."""
    agents = ["aria", "rex", "nova", "zara"]
    
    # 1. Load DB and ensure the transcript array exists
    db = await read_db()
    if "transcripts" not in db:
        db["transcripts"] = {}
        
    if debate_id not in db["transcripts"]:
        db["transcripts"][debate_id] = []
        await write_db(db)
        
    problem_text = db["problems"].get(problem_id, "Analyze this situation.")
    
    try:
        for r in range(1, rounds + 1):
            for i, agent in enumerate(agents):
                # Reload DB to get the absolute latest transcript for context
                db = await read_db()
                current_transcript = db["transcripts"][debate_id]
                
                # Build context for the LLM
                history_context = "\n".join([f"{t['agent']}: {t['message']}" for t in current_transcript])
                if not history_context:
                    history_context = "You are the first to speak."

                # Call Groq
                llm_response = await generate_agent_turn(agent, r, problem_text, history_context)
                
                # Enforce Schema
                turn_data = DebateTurnData(
                    turn_id=f"turn_{uuid.uuid4().hex[:8]}",
                    agent=agent,
                    round=r,
                    message=llm_response.get("message", "Error parsing argument."),
                    targets=llm_response.get("targets", []),
                    timestamp=datetime.utcnow().isoformat() + "Z"
                )
                
                # Save turn to JSON file immediately
                db["transcripts"][debate_id].append(turn_data.model_dump())
                await write_db(db)
                
                # Stream to Frontend
                yield f"event: debate_turn\ndata: {turn_data.model_dump_json()}\n\n"

        # 3. Call Groq for the Final Verdict
        db = await read_db()
        final_history = "\n".join([f"{t['agent']}: {t['message']}" for t in db["transcripts"][debate_id]])
        verdict_json = await generate_final_verdict(problem_text, final_history)
        
        end_data = DebateEndData(**verdict_json)
        
        # Save final verdict to JSON file
        if debate_id not in db["debates"]:
            db["debates"][debate_id] = {}
            
        db["debates"][debate_id]["final_result"] = end_data.model_dump()
        db["debates"][debate_id]["status"] = "completed"
        await write_db(db)
        
        # Stream End Event
        yield f"event: debate_end\ndata: {end_data.model_dump_json()}\n\n"

    except Exception as e:
        error_payload = json.dumps({"message": f"Groq generation failed: {str(e)}"})
        yield f"event: error\ndata: {error_payload}\n\n"