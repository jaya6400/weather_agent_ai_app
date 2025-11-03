# Chain Of Thought Prompting
from dotenv import load_dotenv
from google import genai
from google.genai import types
import requests
from pydantic import BaseModel, Field
from typing import Optional
import json
import os
import time

load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')

client = genai.Client(
    api_key=gemini_api_key
)

def run_command(cmd: str):
    result = os.system(cmd)
    return result


def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    
    return "Something went wrong"

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
}


SYSTEM_PROMPT = """
    You're an expert AI Assistant that resolves user queries efficiently.
    
    Rules:
    - Strictly Follow the given JSON output format
    - Complete tasks in EXACTLY 3 steps maximum: PLAN -> TOOL/ACTION -> OUTPUT
    - Be direct and efficient. No unnecessary planning steps.

    Output JSON Format:
    { "step": "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input": "string" }

    Available Tools:
    - get_weather(city: str): Takes city name as an input string and returns the weather info about the city.
    - run_command(cmd: str): Takes a system linux command as string and executes the command on user's system and returns the output from that command
    
    Example Flow:
    USER: What is the weather of Delhi?
    
    Step 1 - PLAN: { "step": "PLAN", "content": "User needs Delhi weather. Will call get_weather tool." }
    Step 2 - TOOL: { "step": "TOOL", "tool": "get_weather", "input": "delhi" }
    [SYSTEM PROVIDES: The weather in delhi is Partly Cloudy 20°C]
    Step 3 - OUTPUT: { "step": "OUTPUT", "content": "The current weather in Delhi is Partly Cloudy with temperature of 20°C." }
"""

print("\n\n\n")

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Example: PLAN, OUTPUT, TOOL")
    content: Optional[str] = Field(None, description="The optional string content for the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call.")
    input: Optional[str] = Field(None, description="The input params for the tool")

conversation = []

while True:
    user_query = input("🧐💭 ")
    
    conversation.append(f"USER: {user_query}")
    
    step_count = 0
    max_steps = 5  # Safety limit
    
    while step_count < max_steps:
        step_count += 1
        
        # Build prompt
        full_prompt = SYSTEM_PROMPT + "\n\n" + "\n".join(conversation) + "\nASSISTANT:"
        
        try:
            time.sleep(1)  # Rate limiting
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MyOutputFormat
                )
            )

            raw_result = response.text
            
            # Parse JSON response
            try:
                parsed_result = json.loads(raw_result)
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON response")
                break

            current_step = parsed_result.get("step")
            
            if current_step == "PLAN":
                print(f"🧠 Step {step_count}: {parsed_result.get('content')}")
                conversation.append(f"ASSISTANT: {raw_result}")
                continue

            elif current_step == "TOOL":
                tool_to_call = parsed_result.get("tool")
                tool_input = parsed_result.get("input")
                print(f"🛠️  Step {step_count}: Calling {tool_to_call}({tool_input})")
                
                conversation.append(f"ASSISTANT: {raw_result}")
                
                # Execute tool
                tool_response = available_tools[tool_to_call](tool_input)
                print(f"   ↳ Result: {tool_response}")
                
                # Add observation to conversation
                observe_msg = json.dumps({
                    "step": "OBSERVE",
                    "tool": tool_to_call,
                    "output": tool_response
                })
                conversation.append(f"SYSTEM: {observe_msg}")
                continue

            elif current_step == "OUTPUT":
                print(f"🤖 Step {step_count}: {parsed_result.get('content')}")
                conversation.append(f"ASSISTANT: {raw_result}")
                break
                
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("⏳ Rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                continue
            else:
                print(f"❌ Error: {e}")
                break
    
    print()  