import json
import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["GET"], # Allows only GET requests
    allow_headers=["*"],  # Allows all headers
)

# Load student marks from the JSON file
# Assuming q-vercel-python.json is in the root of the project,
# and the script is run from the root or the path is relative to the script.
# For Vercel, files are typically relative to the root of the deployment.
data_file_path = os.path.join(os.path.dirname(__file__), '..', 'q-vercel-python.json')
if not os.path.exists(data_file_path):
    # Fallback for local development if api/index.py is in the root
    data_file_path = 'q-vercel-python.json'

student_marks = {}
try:
    with open(data_file_path, 'r') as f:
        student_marks = json.load(f)
except FileNotFoundError:
    print(f"Error: The file {data_file_path} was not found.")
    # In a real app, you might want to raise an exception or handle this more gracefully
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {data_file_path}.")
    # Handle malformed JSON

@app.get("/api")
async def get_student_marks(name: List[str] = Query(None)):
    marks_response = []
    if name:
        for student_name in name:
            marks_response.append(student_marks.get(student_name, None)) # Return None if student not found
    return {"marks": marks_response}

# Optional: A root endpoint for basic testing
@app.get("/")
def read_root():
    return {"message": "Welcome to the Student Marks API. Use /api?name=X&name=Y to get marks."}