# Weather Agent AI App

A chain-of-thought AI agent powered by Google Gemini that can fetch weather information and execute system commands through natural language queries.

## Features

- 🤖 Chain-of-thought reasoning with structured planning
- 🌤️ Real-time weather information using wttr.in API
- 💻 System command execution capability
- 🔄 Automatic tool selection and execution
- ⚡ Rate limiting to prevent API quota exhaustion
- 📝 JSON-structured responses using Pydantic models

## Prerequisites

- Python 3.8+
- Google Gemini API key

## Screenshot
- <Image width="671" height="335" alt="Capture" src="https://github.com/user-attachments/assets/8486384e-3a42-4d2e-bf1c-00881516f886" />


## Installation

1. Clone the repository:
```bash
git clone https://github.com/jaya6400/weather_agent_ai_app.git
cd weather_agent_ai_app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install google-genai python-dotenv requests pydantic
```

4. Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Usage

Run the agent:
```bash
python file.py
```

### Example Queries
```
👉🏻 what is the weather in ranchi
🧠 Step 1: User needs Ranchi weather. Will call get_weather tool.
🛠️  Step 2: Calling get_weather(ranchi)
   ↳ Result: The weather in ranchi is Clear 15°C
🤖 Step 3: The current weather in Ranchi is Clear with a temperature of 15°C.

👉🏻 what is the weather in delhi
👉🏻 solve 2 + 3 * 5
```

## How It Works

The agent follows a 3-step chain-of-thought process:

1. **PLAN**: Analyzes the user query and determines the action needed
2. **TOOL**: Executes the appropriate tool (get_weather or run_command)
3. **OUTPUT**: Returns the final result to the user

## Available Tools

- `get_weather(city: str)`: Fetches current weather information for a city
- `run_command(cmd: str)`: Executes system commands (use with caution)

## Rate Limiting

The agent includes built-in rate limiting:
- 1-second delay between API calls
- Automatic retry with 10-second wait on 429 errors
- Maximum 5 steps per query to prevent infinite loops

## Project Structure
```
weather_agent_ai_app/
├── agent.py           # Main agent script
├── .env              # Environment variables (API keys)
├── .gitignore        # Git ignore file
└── README.md         # This file
```

## Configuration

You can modify these settings in `agent.py`:

- `max_steps = 5`: Maximum iterations per query
- `time.sleep(1)`: Delay between API calls (in seconds)
- `model="gemini-2.0-flash-exp"`: Gemini model to use

## Safety Notes

⚠️ **Warning**: The `run_command` tool can execute system commands. Use with caution and avoid running untrusted commands.

## Troubleshooting

**Rate Limit Errors (429)**:
- The agent automatically handles these with retries
- If persistent, increase the delay in `time.sleep()`

**API Key Issues**:
- Ensure your `.env` file contains a valid `GEMINI_API_KEY`
- Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Powered by [Google Gemini](https://ai.google.dev/)
- Weather data from [wttr.in](https://wttr.in/)
