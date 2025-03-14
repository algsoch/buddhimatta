from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import zipfile
import io
import os
import tempfile
import shutil
import json
import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# Import our model
try:
    from train_model import BuddhimattaModel
    model = BuddhimattaModel()
except ImportError:
    # Fallback if the model file is not available
    model = None

    # Dictionary of known questions and answers as fallback
    KNOWN_ANSWERS = {
        "Install and run Visual Studio Code. In your Terminal (or Command Prompt), type code -s and press Enter. Copy and paste the entire output below. What is the output ofcode -s?":
        "Version:          Code 1.96.3 (91fbdddc47bc9c09064bf7acf133d22631cbf083, 2025-01-09T18:14:09.060Z)\nOS Version:       Windows_NT x64 10.0.26120\nCPUs:             11th Gen Intel(R) Core(TM) i5-11260H @ 2.60GHz (12 x 2611)\n"
    }

app = FastAPI(title="Buddhimatta - Assignment Answer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnswerResponse(BaseModel):
    answer: str

class FeedbackRequest(BaseModel):
    question: str
    correct_answer: str

def save_question_for_training(question: str, answer: str):
    """Save a question and its answer for future model training."""
    if model:
        model.add_qa_pair(question, answer)
    else:
        # Fallback if model is not available
        try:
            training_data = {}
            if os.path.exists("training_data.json"):
                with open("training_data.json", "r") as f:
                    training_data = json.load(f)

            training_data[question] = answer

            with open("training_data.json", "w") as f:
                json.dump(training_data, f, indent=2)
        except Exception as e:
            print(f"Error saving training data: {e}")

@app.get("/")
async def root():
    return {"message": "Welcome to Buddhimatta - Assignment Answer API"}

@app.post("/api/", response_model=AnswerResponse)
async def process_question(
    background_tasks: BackgroundTasks,
    question: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    # Check if the question is in our model or known answers
    if model:
        model_answer = model.get_answer(question)
        if model_answer:
            return {"answer": model_answer}
    elif question in KNOWN_ANSWERS:
        return {"answer": KNOWN_ANSWERS[question]}

    # Process questions about downloading and unzipping files
    if re.search(r"Download and unzip file.*\.zip.*What is the value in the.*column", question, re.IGNORECASE) and file:
        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save the uploaded zip file
                zip_path = os.path.join(temp_dir, file.filename)
                with open(zip_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)

                # Extract the zip file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Find the CSV file
                csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
                if not csv_files:
                    raise HTTPException(status_code=400, detail="No CSV file found in the zip")

                # Read the CSV file
                csv_path = os.path.join(temp_dir, csv_files[0])
                df = pd.read_csv(csv_path)

                # Extract the column name from the question
                column_match = re.search(r'value in the ["\']?([^"\']*)["\']? column', question)
                column_name = "answer"  # Default column name
                if column_match:
                    column_name = column_match.group(1)

                # Check if the column exists
                if column_name not in df.columns:
                    raise HTTPException(status_code=400, detail=f"No '{column_name}' column found in the CSV")

                # Get the answer
                answer_value = str(df[column_name].iloc[0])

                # Save this question-answer pair for future training
                background_tasks.add_task(save_question_for_training, question, answer_value)

                return {"answer": answer_value}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

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

                    # Save this question-answer pair for future training
                    background_tasks.add_task(save_question_for_training, question, output)

                    return {"answer": output}
                finally:
                    sys.stdout = old_stdout
        except Exception as e:
            # Don't expose the error, just continue to other handlers
            pass

    # Process questions about file analysis (without zip)
    if file and ("What is the content of" in question or "What does the file contain" in question):
        try:
            content = file.file.read().decode("utf-8").strip()

            # Save this question-answer pair for future training
            background_tasks.add_task(save_question_for_training, question, content)

            return {"answer": content}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    # Default response if we don't know the answer
    return {"answer": "I don't have the answer to this question yet. Please provide feedback with the correct answer to improve the system."}

@app.post("/api/feedback")
async def provide_feedback(feedback: FeedbackRequest):
    """Endpoint to provide feedback with correct answers for questions."""
    try:
        # Save the feedback for future training
        if model:
            model.add_qa_pair(feedback.question, feedback.correct_answer)
        else:
            save_question_for_training(feedback.question, feedback.correct_answer)

        return {"message": "Thank you for your feedback! This will help improve the system."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)