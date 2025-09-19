import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found in .env file. Gemini functions may not work.")

# Configure Groq API
GROQ_API_KEY = os.getenv("GroqAPIKey")
groq_client = None
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    print("Warning: GroqAPIKey not found in .env file. Groq functions may not work.")


def query_gemini(prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    Sends a prompt to the Gemini API and returns the response text.
    """
    if not GEMINI_API_KEY:
        return "Gemini API key is not configured."

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return f"An error occurred with the Gemini API: {e}"

def query_groq(prompt: str, model: str = "llama3-8b-8192") -> str:
    """
    Sends a prompt to the Groq API and returns the response text.
    """
    if not groq_client:
        return "Groq API key is not configured."

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq API error: {e}")
        return f"An error occurred with the Groq API: {e}"
