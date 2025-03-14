import json
import os

class BuddhimattaModel:
    """
    A simple model that stores question-answer pairs and can be expanded over time.
    This is a placeholder for a more sophisticated model that could be trained on more data.
    """
    
    def __init__(self, data_file="model_data.json"):
        self.data_file = data_file
        self.qa_pairs = {}
        self.load_data()
    
    def load_data(self):
        """Load existing question-answer pairs if available."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.qa_pairs = json.load(f)
                print(f"Loaded {len(self.qa_pairs)} question-answer pairs from {self.data_file}")
            except Exception as e:
                print(f"Error loading data: {e}")
                self.qa_pairs = {}
        else:
            # Initialize with default data
            self.qa_pairs = {
                "Install and run Visual Studio Code. In your Terminal (or Command Prompt), type code -s and press Enter. Copy and paste the entire output below. What is the output ofcode -s?": 
                "Version:          Code 1.96.3 (91fbdddc47bc9c09064bf7acf133d22631cbf083, 2025-01-09T18:14:09.060Z)\nOS Version:       Windows_NT x64 10.0.26120\nCPUs:             11th Gen Intel(R) Core(TM) i5-11260H @ 2.60GHz (12 x 2611)\n"
            }
            self.save_data()
    
    def save_data(self):
        """Save the current question-answer pairs to the data file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.qa_pairs, f, indent=2)
            print(f"Saved {len(self.qa_pairs)} question-answer pairs to {self.data_file}")
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_qa_pair(self, question, answer):
        """Add a new question-answer pair to the model."""
        self.qa_pairs[question] = answer
        self.save_data()
        print(f"Added new question-answer pair. Total pairs: {len(self.qa_pairs)}")
    
    def get_answer(self, question):
        """Get the answer for a given question if it exists."""
        return self.qa_pairs.get(question, None)
    
    def train(self, new_qa_pairs):
        """Train the model with new question-answer pairs."""
        for question, answer in new_qa_pairs.items():
            self.add_qa_pair(question, answer)
        print(f"Training complete. Model now has {len(self.qa_pairs)} question-answer pairs.")

if __name__ == "__main__":
    # Example usage
    model = BuddhimattaModel()
    
    # Add some example training data
    training_data = {
        "What is the capital of France?": "Paris",
        "What is 2+2?": "4"
    }
    
    # Train the model with the new data
    model.train(training_data)
    
    # Test the model
    test_questions = [
        "What is the capital of France?",
        "What is 2+2?",
        "Install and run Visual Studio Code. In your Terminal (or Command Prompt), type code -s and press Enter. Copy and paste the entire output below. What is the output ofcode -s?"
    ]
    
    for question in test_questions:
        answer = model.get_answer(question)
        if answer:
            print(f"Q: {question}")
            print(f"A: {answer}")
            print("-" * 50)
        else:
            print(f"No answer found for: {question}")