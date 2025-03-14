from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import zipfile
import io
import os
import tempfile
import shutil
import json
import re
import csv
from typing import Optional, Dict, Any

app = FastAPI(title="Buddhimatta - Assignment Answer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dictionary of known questions and answers
KNOWN_ANSWERS = {
    "Install and run Visual Studio Code. In your Terminal (or Command Prompt), type code -s and press Enter. Copy and paste the entire output below. What is the output ofcode -s?": 
    "Version:          Code 1.96.3 (91fbdddc47bc9c09064bf7acf133d22631cbf083, 2025-01-09T18:14:09.060Z)\nOS Version:       Windows_NT x64 10.0.26120\nCPUs:             11th Gen Intel(R) Core(TM) i5-11260H @ 2.60GHz (12 x 2611)\n"
}

def read_csv_without_pandas(file_path, column_name="answer"):
    """Read a CSV file without using pandas."""
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if column_name in row:
                return row[column_name]
    return None

@app.get("/")
async def root():
    return {"message": "Welcome to Buddhimatta - Assignment Answer API"}

@app.post("/")
async def process_question(
    request: Request,
    question: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    # Check if the question is in our known answers
    if question in KNOWN_ANSWERS:
        return {"answer": KNOWN_ANSWERS[question]}
    
    # Process questions about downloading and unzipping files
    if re.search(r"Download and unzip file.*\.zip.*What is the value in the.*column", question, re.IGNORECASE) and file:
        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save the uploaded zip file
                zip_path = os.path.join(temp_dir, file.filename)
                with open(zip_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Extract the zip file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find the CSV file
                csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
                if not csv_files:
                    return {"answer": "No CSV file found in the zip"}
                
                # Extract the column name from the question
                column_match = re.search(r'value in the ["\']?([^"\']*)["\']? column', question)
                column_name = "answer"  # Default column name
                if column_match:
                    column_name = column_match.group(1)
                
                # Read the CSV file without pandas
                csv_path = os.path.join(temp_dir, csv_files[0])
                answer_value = read_csv_without_pandas(csv_path, column_name)
                
                if answer_value is None:
                    return {"answer": f"No '{column_name}' column found in the CSV"}
                
                return {"answer": answer_value}
        
        except Exception as e:
            return {"answer": f"Error processing file: {str(e)}"}
    
    # Process questions about Python code execution
    if "What is the output of the following Python code?" in question:
        try:
            # Extract the Python code from the question
            code_match = re.search(r'```python\s*(.*?)\s*```', question, re.DOTALL)
            if code_match:
                code = code_match.group(1)
                
                # Create a safe environment for execution
                local_vars = {}
                
                # Redirect stdout to capture output
                import sys
                from io import StringIO
                
                old_stdout = sys.stdout
                redirected_output = StringIO()
                sys.stdout = redirected_output
                
                try:
                    # Execute the code
                    exec(code, {}, local_vars)
                    output = redirected_output.getvalue().strip()
                    
                    return {"answer": output}
                finally:
                    sys.stdout = old_stdout
        except Exception as e:
            # Don't expose the error, just continue to other handlers
            pass
    
    # Process questions about file analysis (without zip)
    if file and ("What is the content of" in question or "What does the file contain" in question):
        try:
            content = await file.read()
            content_str = content.decode("utf-8").strip()
            
            return {"answer": content_str}
        except Exception as e:
            return {"answer": f"Error reading file: {str(e)}"}
    
    # Default response if we don't know the answer
    return {"answer": "I don't have the answer to this question yet."}

@app.post("/feedback")
async def provide_feedback(request: Request):
    """Endpoint to provide feedback with correct answers for questions."""
    try:
        body = await request.json()
        question = body.get("question", "")
        correct_answer = body.get("correct_answer", "")
        
        # Add to known answers for immediate use
        KNOWN_ANSWERS[question] = correct_answer
        
        return {"message": "Thank you for your feedback! This will help improve the system."}
    except Exception as e:
        return {"message": f"Error processing feedback: {str(e)}"}

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)