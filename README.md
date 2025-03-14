# Buddhimatta - Assignment Answer API

An API that automatically answers questions from graded assignments for the Tools in Data Science course at IIT Madras' Online Degree in Data Science program.

## Features

- Accepts questions from any of the 5 graded assignments
- Processes file attachments when needed
- Returns answers in a standardized JSON format
- Easy to deploy on platforms like Vercel

## API Usage

The API accepts POST requests with the following parameters:

- `question`: The assignment question (required)
- `file`: An optional file attachment (e.g., ZIP files that need to be processed)

### Example Request

```bash
curl -X POST "https://your-app.vercel.app/api/" \
  -H "Content-Type: multipart/form-data" \
  -F "question=Download and unzip file abcd.zip which has a single extract.csv file inside. What is the value in the \"answer\" column of the CSV file?" \
  -F "file=@abcd.zip"
```

### Example Response

```json
{
  "answer": "1234567890"
}
```

## Local Development

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the server:
   ```
   uvicorn main:app --reload
   ```
4. The API will be available at `http://localhost:8000/api/`

## Deployment

This application can be deployed to any platform that supports Python applications, such as:

- Vercel
- Heroku
- AWS Lambda
- Google Cloud Run

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.