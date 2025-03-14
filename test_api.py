import requests
import json
import os
from pathlib import Path
import tempfile
import zipfile
import pandas as pd

# URL of your deployed API
API_URL = "http://localhost:8000/api/"  # Change this to your deployed URL

def test_known_question():
    """Test a known question that should be in the model."""
    question = "Install and run Visual Studio Code. In your Terminal (or Command Prompt), type code -s and press Enter. Copy and paste the entire output below. What is the output ofcode -s?"
    
    response = requests.post(
        API_URL,
        data={"question": question},
        files={}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Verify the response
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "Version:" in response.json()["answer"]
    
    print("✅ Known question test passed!")

def test_csv_in_zip():
    """Test a question that requires extracting a CSV from a ZIP file."""
    # Create a temporary CSV file
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a CSV file
        csv_path = os.path.join(temp_dir, "extract.csv")
        df = pd.DataFrame({"answer": ["This is the answer!"]})
        df.to_csv(csv_path, index=False)
        
        # Create a ZIP file containing the CSV
        zip_path = os.path.join(temp_dir, "test.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(csv_path, arcname="extract.csv")
        
        # Send the request
        question = "Download and unzip file test.zip which has a single extract.csv file inside. What is the value in the \"answer\" column of the CSV file?"
        
        with open(zip_path, 'rb') as zip_file:
            response = requests.post(
                API_URL,
                data={"question": question},
                files={"file": ("test.zip", zip_file, "application/zip")}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Verify the response
        assert response.status_code == 200
        assert "answer" in response.json()
        assert response.json()["answer"] == "This is the answer!"
        
        print("✅ CSV in ZIP test passed!")

def test_python_code_execution():
    """Test a question that requires executing Python code."""
    question = """What is the output of the following Python code?
```python
for i in range(5):
    print(i * 2)
```"""
    
    response = requests.post(
        API_URL,
        data={"question": question},
        files={}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Verify the response
    assert response.status_code == 200
    assert "answer" in response.json()
    assert response.json()["answer"] == "0\n2\n4\n6\n8"
    
    print("✅ Python code execution test passed!")

def test_feedback():
    """Test providing feedback with a correct answer."""
    question = "What is the capital of France?"
    correct_answer = "Paris"
    
    response = requests.post(
        API_URL + "feedback",
        json={"question": question, "correct_answer": correct_answer}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Verify the response
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Now test if the feedback was incorporated
    response = requests.post(
        API_URL,
        data={"question": question},
        files={}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Verify the response
    assert response.status_code == 200
    assert "answer" in response.json()
    assert response.json()["answer"] == "Paris"
    
    print("✅ Feedback test passed!")

if __name__ == "__main__":
    print("Running API tests...")
    
    try:
        test_known_question()
        test_csv_in_zip()
        test_python_code_execution()
        test_feedback()
        
        print("\n🎉 All tests passed! Your API is working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("Please check your API implementation and try again.")