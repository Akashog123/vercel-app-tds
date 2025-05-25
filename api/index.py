import json
import os
import logging # Added logging
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
student_marks = {}
# Construct the path robustly
data_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'q-vercel-python.json'))
logger.info(f"Attempting to load student data from: {data_file_path}")

try:
    with open(data_file_path, 'r') as f:
        loaded_data = json.load(f)
        # Convert list of objects to dictionary: {name: marks}
        if isinstance(loaded_data, list):
            student_marks = {item['name']: item['marks'] for item in loaded_data if isinstance(item, dict) and 'name' in item and 'marks' in item}
            logger.info(f"Successfully loaded and processed student data from {data_file_path}. {len(student_marks)} records loaded.")
        else:
            # If the JSON was already in the {name: marks} format, use it directly (though q-vercel-python.json is a list)
            # This part is less likely to be hit given the current q-vercel-python.json structure but adds robustness
            student_marks = loaded_data 
            logger.info(f"Successfully loaded student data (expected pre-formatted dict) from {data_file_path}.")

except FileNotFoundError:
    logger.error(f"Error: The file {data_file_path} was not found.")
    logger.error(f"Current script file location (__file__): {__file__}")
    logger.error(f"Current working directory (os.getcwd()): {os.getcwd()}")
except json.JSONDecodeError as e:
    logger.error(f"Error: Could not decode JSON from {data_file_path}. Details: {e}")
except Exception as e:
    logger.error(f"An unexpected error occurred while loading {data_file_path}: {e}")

@app.get("/api")
async def get_student_marks(name: List[str] = Query(None)):
    marks_response = []
    if not student_marks: # Check if student_marks is empty due to loading failure
        logger.warning("/api endpoint called but student_marks data is not available or empty.")
        # Optionally, return an error response or an empty list with a specific message
        # For now, it will proceed and likely return None for all names if student_marks is empty
    
    if name:
        for student_name in name:
            marks = student_marks.get(student_name)
            if marks is None:
                logger.info(f"Student '{student_name}' not found in records.")
            marks_response.append(marks) 
    else: # If no names are provided, perhaps return all data or a message
        logger.info("/api called without specific names. Returning empty list as per current logic for 'name' parameter.")
        # If you want to return all marks when no name is specified, this logic would need to change.
        # For example: return student_marks
    return {"marks": marks_response}

# Optional: A root endpoint for basic testing
@app.get("/")
def read_root():
    return {"message": "Welcome to the Student Marks API. Use /api?name=X&name=Y to get marks."}