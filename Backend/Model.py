import cohere
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

COHERE_API_KEY = os.getenv("CohereAPIKey")
co = None
if COHERE_API_KEY:
    co = cohere.Client(api_key=COHERE_API_KEY)
else:
    print("Warning: CohereAPIKey not found in .env file. Model functions may not work.")

# A more concise and structured preamble
preamble = """
You are a highly intelligent decision-making model for a voice assistant. Your task is to analyze a user's query and break it down into one or more executable tasks.

You must respond with a JSON array of objects. Each object represents a single task and must have two keys: "tool" and "query".

- The "tool" key must be one of the following strings: "exit", "general", "realtime", "open", "close", "play", "generate image", "system", "content", "googlesearch", "youtubesearch", "reminder", "wakeup".
- The "query" key should be the corresponding user query for that tool.

Here are some examples:

User: "open chrome and tell me about sashi tharoor?"
Response:
[
  {"tool": "open", "query": "chrome"},
  {"tool": "general", "query": "tell me about sashi tharoor?"}
]

User: "search narendra modi"
Response:
[
  {"tool": "googlesearch", "query": "narendra modi"},
  {"tool": "realtime", "query": "narendra modi"}
]

User: "what is today's date and remind me about my doctor's appointment at 5pm"
Response:
[
  {"tool": "general", "query": "what is today's date"},
  {"tool": "reminder", "query": "doctor's appointment at 5pm"}
]

User: "hello"
Response:
[
  {"tool": "wakeup", "query": "hello"}
]

If you cannot determine the tool, default to "general". Do not add any text outside of the JSON array.
"""

ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": '[{"tool": "general", "query": "how are you?"}]'},
    {"role": "User", "message": "open chrome and firefox?"},
    {"role": "Chatbot", "message": '[{"tool": "open", "query": "chrome"}, {"tool": "open", "query": "firefox"}]'},
]

def FirstLayerDMM(prompt: str = "test"):
    if not co:
        return [f"general {prompt}"] # Default behavior if Cohere is not configured

    try:
        stream = co.chat_stream(
            model='command-r-plus',
            message=prompt,
            temperature=0.3,
            chat_history=ChatHistory,
            prompt_truncation='OFF',
            preamble=preamble
        )

        response_text = ""
        for event in stream:
            if event.event_type == "text-generation":
                response_text += event.text

        # Clean up the response to get only the JSON part
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if not json_match:
            print(f"Warning: Could not find a JSON array in the model's response: {response_text}")
            return [f"general {prompt}"]

        json_string = json_match.group(0)

        # Parse the JSON response
        tasks = json.loads(json_string)

        # Convert the list of dicts to a list of lists for compatibility with the rest of the system
        decision = []
        for task in tasks:
            if isinstance(task, dict) and "tool" in task and "query" in task:
                decision.append(f"{task['tool']} {task['query']}")

        if not decision:
             print(f"Warning: Parsed JSON is empty or invalid: {tasks}")
             return [f"general {prompt}"]

        return decision

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from model response: {e}\nResponse was: {response_text}")
        return [f"general {prompt}"] # Fallback on JSON error
    except Exception as e:
        print(f"An unexpected error occurred in FirstLayerDMM: {e}")
        return [f"general {prompt}"] # Fallback on any other error

if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        if user_input.lower() == "exit":
            break
        print(FirstLayerDMM(user_input))
