import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def test_connection():
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents="Say 'connection successful' and nothing else."
    )
    return response.text

if __name__ == "__main__":
    print(test_connection())