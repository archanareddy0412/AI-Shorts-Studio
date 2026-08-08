from google import genai
from dotenv import load_dotenv
import os

load_dotenv(r"..\AI-Youtube-Shorts-Generator-main\.env")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    vertexai=False,
)
response = client.models.generate_content(
   model="models/gemini-3.6-flash",
    contents="Reply with only: Hello"
)

print(response.text)