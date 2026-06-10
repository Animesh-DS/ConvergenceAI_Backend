import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

print("🔥 STARTING END-TO-END TEST 🔥\n")

# 1. Create a dummy file for the parser
file_name = "test_dilemma.txt"
with open(file_name, "w") as f:
    f.write("Dilemma: We need to decide if we should migrate our legacy monolithic database to a distributed microservices architecture by Q3. Our engineering team is at 90% capacity, but server costs are rising.")

# 2. Test Endpoint A: Upload
print("--- 1. TESTING FILE UPLOAD ---")
with open(file_name, "rb") as f:
    files = {"file": (file_name, f, "text/plain")}
    upload_res = requests.post(f"{BASE_URL}/upload", files=files)

upload_data = upload_res.json()
print(json.dumps(upload_data, indent=2))
problem_id = upload_data.get("problem_id")

if not problem_id:
    print("❌ Upload failed. Stopping test.")
    exit()

time.sleep(1)

# 3. Test Endpoint B: Start Debate
print("\n--- 2. STARTING DEBATE ---")
start_res = requests.post(f"{BASE_URL}/start-debate", json={"problem_id": problem_id, "rounds": 2})
debate_data = start_res.json()
print(json.dumps(debate_data, indent=2))
debate_id = debate_data.get("debate_id")

time.sleep(1)

# 4. Test Endpoint C: Stream Debate (Live Groq Calls)
print("\n--- 3. STREAMING LIVE GROQ DEBATE (This will take a few seconds) ---")
stream_res = requests.get(f"{BASE_URL}/stream-debate/{debate_id}", stream=True)

for line in stream_res.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        # Print the raw SSE event exactly as the browser will receive it
        print(decoded_line)
        
        # Add a visual separator when a JSON data block finishes
        if decoded_line.startswith("data: "):
            print("-" * 50)

time.sleep(1)

# 5. Test Endpoint D: Fetch Final History
print("\n--- 4. FETCHING FINAL DATABASE RECORD ---")
result_res = requests.get(f"{BASE_URL}/result/{debate_id}")
print(json.dumps(result_res.json(), indent=2))

print("\n✅ TEST COMPLETE.")