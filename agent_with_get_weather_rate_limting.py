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
    You're an expert AI Assistant in resolving user queries using chain of thought.
    You work on START, PLAN and OUTPUT steps.
    You need to first PLAN what needs to be done. The PLAN can be multiple steps.
    Once you think enough PLAN has been done, finally you can give an OUTPUT.
    You can also call a tool if required from the list of available tools.
    for every tool call wait for the observe step which is the output from the called tool.

    Rules:
    - Strictly Follow the given JSON output format
    - Only run one step at a time.
    - The sequence of steps is START (where user gives an input), PLAN (That can be multiple times) and finally OUTPUT (which is going to the displayed to the user).
    - IMPORTANT: Keep your planning steps concise. Don't create more than 3-4 PLAN steps before taking action.

    Output JSON Format:
    { "step": "START" | "PLAN" | "OUTPUT" | "TOOL", "content": "string", "tool": "string", "input": "string" }

    Available Tools:
    - get_weather(city: str): Takes city name as an input string and returns the weather info about the city.
    - run_command(cmd: str): Takes a system linux command as string and executes the command on user's system and returns the output from that command
    
    Example 1:
    START: Hey, Can you solve 2 + 3 * 5 / 10
    PLAN: { "step": "PLAN", "content": "User wants to solve a math problem using BODMAS" }
    PLAN: { "step": "PLAN", "content": "First multiply: 3 * 5 = 15, then divide: 15 / 10 = 1.5, then add: 2 + 1.5 = 3.5" }
    OUTPUT: { "step": "OUTPUT", "content": "3.5" }

    Example 2:
    START: What is the weather of Delhi?
    PLAN: { "step": "PLAN", "content": "User wants weather info for Delhi. I should use get_weather tool." }
    TOOL: { "step": "TOOL", "tool": "get_weather", "input": "delhi" }
    OBSERVE: { "step": "OBSERVE", "tool": "get_weather", "output": "The temp of delhi is cloudy with 20 C" }
    OUTPUT: { "step": "OUTPUT", "content": "The current weather in Delhi is 20°C with cloudy sky." }
    
"""

print("\n\n\n")

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Example: PLAN, OUTPUT, TOOL, etc")
    content: Optional[str] = Field(None, description="The optional string content for the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call.")
    input: Optional[str] = Field(None, description="The input params for the tool")

message_history = []
max_iterations = 10  # Prevent infinite loops

while True:
    user_query = input("👉🏻 ")
    
    # Build the full prompt with system prompt and conversation history
    full_prompt = SYSTEM_PROMPT + "\n\nConversation History:\n"
    for msg in message_history[-10:]:  # Keep only last 10 messages to reduce token usage
        full_prompt += f"{msg['role'].upper()}: {msg['content']}\n"
    full_prompt += f"USER: {user_query}\nASSISTANT:"
    
    message_history.append({ "role": "user", "content": user_query })

    iteration_count = 0
    
    while iteration_count < max_iterations:
        iteration_count += 1
        
        try:
            # Add delay to avoid rate limiting
            time.sleep(1)
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MyOutputFormat
                )
            )

            raw_result = response.text
            message_history.append({"role": "assistant", "content": raw_result})
            
            # Parse JSON response
            try:
                parsed_result = json.loads(raw_result)
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON response")
                break

            if parsed_result.get("step") == "START":
                print("🔥", parsed_result)
                continue

            if parsed_result.get("step") == "TOOL":
                tool_to_call = parsed_result.get("tool")
                tool_input = parsed_result.get("input")
                print(f"🛠️: {tool_to_call} ({tool_input})")

                tool_response = available_tools[tool_to_call](tool_input)
                print(f"🛠️: {tool_to_call} ({tool_input}) = {tool_response}")
                
                observe_msg = json.dumps({
                    "step": "OBSERVE",
                    "tool": tool_to_call,
                    "input": tool_input,
                    "output": tool_response
                })
                message_history.append({ "role": "system", "content": observe_msg })
                
                # Rebuild prompt with new observation
                full_prompt = SYSTEM_PROMPT + "\n\nConversation History:\n"
                for msg in message_history[-10:]:
                    full_prompt += f"{msg['role'].upper()}: {msg['content']}\n"
                full_prompt += "ASSISTANT:"
                
                continue

            if parsed_result.get("step") == "PLAN":
                print("🧠", parsed_result)
                continue

            if parsed_result.get("step") == "OUTPUT":
                print("🤖", parsed_result)
                break
                
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("⏳ Rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                continue
            else:
                print(f"❌ Error: {e}")
                break
    
    if iteration_count >= max_iterations:
        print("⚠️ Max iterations reached. Stopping.")
