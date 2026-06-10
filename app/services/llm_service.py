import json
from groq import AsyncGroq
from app.core.config import settings

client = AsyncGroq(api_key=settings.GROQ_API_KEY)

# --- System Prompts (P3's Domain) ---
# We explicitly tell the model to return JSON to trigger Groq's JSON mode.
AGENT_PROMPTS = {
    "aria": "You are Aria, the Optimist. Focus on human impact, UX, and market potential.",
    "rex": "You are Rex, the Critic. You aggressively optimize for performance, cost, and strict logic.",
    "nova": "You are Nova, the Data Scientist. You rely purely on historical data, metrics, and wild but viable alternatives.",
    "zara": "You are Zara, the Devil's Advocate. Your sole job is to destroy the other agents' arguments by finding security flaws and edge cases."
}

async def generate_agent_turn(agent: str, round_num: int, problem_text: str, history_context: str) -> dict:
    """Calls Groq to generate a single agent's argument."""
    
    system_instruction = f"""
    {AGENT_PROMPTS[agent]}
    
    You are participating in Round {round_num} of a debate.
    Original Problem: {problem_text}
    
    You MUST output your response in raw JSON format matching this exact schema:
    {{
      "message": "Your concise, punchy argument (under 3 sentences).",
      "targets": ["name_of_agent_you_are_attacking_or_agreeing_with"]
    }}
    """
    
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Previous Debate History:\n{history_context}\n\nGenerate your response in JSON."}
    ]

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        response_format={"type": "json_object"} # Forces valid JSON output
    )
    
    return json.loads(response.choices[0].message.content)

async def generate_final_verdict(problem_text: str, history_context: str) -> dict:
    """Calls Groq to act as the impartial judge and generate the final JSON consensus."""
    
    system_instruction = """
    You are the impartial Convergence Engine. Your job is to read the debate and declare a winner or consensus.
    
    You MUST output your response in raw JSON format matching this exact schema:
    {
      "verdict": "Your 1-2 sentence final decision.",
      "confidence": integer between 0 and 100,
      "summary_by_agent": {
        "aria": "1 sentence summary",
        "rex": "1 sentence summary",
        "nova": "1 sentence summary",
        "zara": "1 sentence summary"
      },
      "winning_argument": "aria" | "rex" | "nova" | "zara" | "consensus"
    }
    """

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Problem: {problem_text}\n\nDebate Transcript:\n{history_context}\n\nGenerate the final verdict in JSON."}
    ]

    response = await client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=messages,
        temperature=0.2, # Low temp for analytical consistency
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)