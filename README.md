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

### Deploying to Vercel

This application is optimized for deployment on Vercel. Follow these steps:

1. Fork or clone this repository to your GitHub account
2. Connect your GitHub repository to Vercel
3. During the import, Vercel will automatically detect the FastAPI application
4. Deploy the application

The API will be available at:
- `https://your-app.vercel.app/api/` - Main API endpoint
- `https://your-app.vercel.app/api/feedback` - Feedback endpoint

### Alternative Deployment Options

You can also deploy this application to other platforms:

- Heroku
- AWS Lambda
- Google Cloud Run

For these platforms, use the `main.py` file instead of the Vercel-specific files.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.