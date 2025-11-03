from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')
# The client gets the API key from the environment variable `GEMINI_API_KEY`

client = genai.Client(
    api_key=gemini_api_key
)

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)