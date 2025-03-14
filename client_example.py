import requests
import sys
import os

# Replace with your deployed API URL
API_URL = "https://your-app.vercel.app/api/"

def ask_question(question, file_path=None):
    """
    Send a question to the API and get the answer.
    
    Args:
        question (str): The question to ask
        file_path (str, optional): Path to a file to upload with the question
        
    Returns:
        str: The answer from the API
    """
    files = {}
    if file_path and os.path.exists(file_path):
        files = {"file": (os.path.basename(file_path), open(file_path, "rb"))}
    
    try:
        response = requests.post(
            API_URL,
            data={"question": question},
            files=files
        )
        
        if response.status_code == 200:
            return response.json()["answer"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        # Close any open file handles
        for file_obj in files.values():
            if hasattr(file_obj[1], 'close'):
                file_obj[1].close()

def provide_feedback(question, correct_answer):
    """
    Provide feedback to the API with the correct answer for a question.
    
    Args:
        question (str): The question
        correct_answer (str): The correct answer
        
    Returns:
        str: The response message from the API
    """
    try:
        response = requests.post(
            API_URL + "feedback",
            json={"question": question, "correct_answer": correct_answer}
        )
        
        if response.status_code == 200:
            return response.json()["message"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("Buddhimatta - Assignment Answer Client")
    print("=====================================")
    
    while True:
        print("\nOptions:")
        print("1. Ask a question")
        print("2. Ask a question with a file")
        print("3. Provide feedback")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            question = input("\nEnter your question: ")
            print("\nThinking...")
            answer = ask_question(question)
            print(f"\nAnswer: {answer}")
            
        elif choice == "2":
            question = input("\nEnter your question: ")
            file_path = input("Enter the path to the file: ")
            print("\nThinking...")
            answer = ask_question(question, file_path)
            print(f"\nAnswer: {answer}")
            
        elif choice == "3":
            question = input("\nEnter the question: ")
            correct_answer = input("Enter the correct answer: ")
            print("\nSending feedback...")
            response = provide_feedback(question, correct_answer)
            print(f"\nResponse: {response}")
            
        elif choice == "4":
            print("\nGoodbye!")
            sys.exit(0)
            
        else:
            print("\nInvalid choice. Please try again.")