import subprocess
import pyautogui
from pathlib import Path
import google.generativeai as genai
import time
import json
import re
import os
from Speech import TextToSpeech as speak  # Assuming this is your TTS module
import asyncio
from google.api_core import exceptions
from dotenv import load_dotenv

load_dotenv()

def parse_command_fallback(command):
    """Fallback regex-based command parser if Gemini fails."""
    platform_match = re.search(r"(whatsapp|telegram)", command.lower())
    platform = platform_match.group(0) if platform_match else "whatsapp"

    recipient_match = re.search(r"(to|on|send)\s+([a-zA-Z]+)", command.lower())
    target_name = recipient_match.group(2) if recipient_match else None

    message_intent = re.sub(r"(send|to|on|whatsapp|telegram)\s+", "", command.lower())
    if target_name:
        message_intent = message_intent.replace(target_name.lower(), "").strip()

    return {
        "platform": platform,
        "recipient": target_name,
        "message_intent": message_intent or "Default message"
    }

def socialmedia(command, max_retries=3):
    # Configure Gemini with API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        speak("Gemini API key is not configured. Please set it in the .env file.")
        return

    genai.configure(api_key=api_key)
    flash = genai.GenerativeModel("gemini-1.5-flash")

    # Try to parse command with Gemini
    parsed = None
    for attempt in range(max_retries):
        try:
            parse_prompt = f"""
            You are Jarvis, an AI assistant. Parse the following command to extract:
            1. The social media platform (whatsapp or telegram).
            2. The recipient's name (a single name or None if not specified).
            3. The message intent (the content of the message, excluding platform and recipient).
            Command: "{command}"
            Return the result as a JSON object with keys: 'platform', 'recipient', 'message_intent'.
            If the platform is not specified or unrecognized, default to 'whatsapp'.
            Example input: "send varun hello monkey on whatsapp"
            Example output: {{"platform": "whatsapp", "recipient": "varun", "message_intent": "hello monkey"}}
            """
            parse_response = flash.generate_content(parse_prompt)
            if parse_response.text:
                parsed = json.loads(parse_response.text.strip())
                break
            else:
                print(f"Empty response from Gemini on attempt {attempt + 1}")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing Gemini response on attempt {attempt + 1}: {e}")
        except exceptions.GoogleAPIError as e:
            print(f"Gemini API error on attempt {attempt + 1}: {e}")
        time.sleep(1)  # Wait before retrying

    # Use fallback parsing if Gemini fails
    if not parsed:
        print("Gemini parsing failed, using regex fallback.")
        parsed = parse_command_fallback(command)

    platform = parsed.get("platform", "whatsapp").lower()
    target_name = parsed.get("recipient")
    message_intent = parsed.get("message_intent", "Default message")

    # Generate the message with Gemini
    message = "Default message"
    try:
        message_prompt = f"""
        You are Jarvis. Generate a concise message for {platform}: '{message_intent}'.
        You are texting on behalf of Sujith. Behave like a human and ensure the message is clear and sensible.
        """
        message_response = flash.generate_content(message_prompt)
        message = message_response.text.strip() if message_response.text else "Default message"
    except exceptions.GoogleAPIError as e:
        print(f"Error generating message with Gemini: {e}")
        message = message_intent  # Fallback to raw intent

    if platform == "whatsapp" and target_name:
        speak("Opening WhatsApp in fullscreen to search for the contact.")
        subprocess.Popen(["start", "whatsapp://"], shell=True)
        time.sleep(3)

        pyautogui.click(x=50, y=50)  # Adjust for WhatsApp search bar
        time.sleep(1)
        pyautogui.typewrite(target_name)
        time.sleep(2)

        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(1)

        speak(f"Typing message to {target_name}.")
        pyautogui.typewrite(message)
        pyautogui.press("enter")
        speak(f"Message sent to {target_name} on WhatsApp.")

    elif platform == "telegram" and target_name:
        speak(f"Opening Telegram in fullscreen for {target_name}.")
        subprocess.Popen(["start", "tg://"], shell=True)
        time.sleep(4)

        pyautogui.click(x=70, y=50)  # Adjust for Telegram search bar
        time.sleep(1)
        pyautogui.typewrite(target_name)
        time.sleep(2)

        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(2)

        pyautogui.click(x=750, y=1000)  # Adjust for Telegram's message input field
        time.sleep(1)

        speak(f"Typing message to {target_name}.")
        pyautogui.typewrite(message)
        time.sleep(1)
        pyautogui.press("enter")
        speak(f"Message sent to {target_name} on Telegram.")

    else:
        speak("No valid recipient or platform specified.")
        return False

    return True

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        if command.startswith("socialmedia "):
            fun = asyncio.to_thread(socialmedia, command.removeprefix("socialmedia "))
            funcs.append(fun)

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

# Test the function
if __name__ == "__main__":
    socialmedia("send varun hello monkey on telegram")
