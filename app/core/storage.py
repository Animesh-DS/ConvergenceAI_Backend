import json
import os
import aiofiles

DB_FILE = "app/data/database.json"

# Initialize the file if it doesn't exist
if not os.path.exists(DB_FILE):
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump({"problems": {}, "debates": {}, "transcripts": {}}, f)

async def read_db() -> dict:
    """Reads the entire JSON database."""
    try:
        async with aiofiles.open(DB_FILE, mode="r") as f:
            content = await f.read()
            return json.loads(content)
    except Exception:
        return {"problems": {}, "debates": {}, "transcripts": {}}

async def write_db(data: dict):
    """Writes the entire dictionary back to the JSON file."""
    async with aiofiles.open(DB_FILE, mode="w") as f:
        await f.write(json.dumps(data, indent=4))