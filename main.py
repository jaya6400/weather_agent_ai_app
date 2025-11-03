from google import genai
from dotenv import load_dotenv
import requests, os

load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')
# The client gets the API key from the environment variable `GEMINI_API_KEY`

client = genai.Client(
    api_key=gemini_api_key
)

def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    
    return "Something went wrong"


def main():
    user_query = input("> ")
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_query
    )

    print(f"🤖: {response.text}")

main()