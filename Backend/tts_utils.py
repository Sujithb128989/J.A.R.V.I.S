import requests
import pygame
import asyncio
import os
import random
from typing import Union

def generate_audio(message: str, voice: str = "Brian") -> Union[None, bytes]:
    """Generates audio from text using the StreamElements API."""
    url: str = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={{{message}}}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

    try:
        result = requests.get(url=url, headers=headers)
        result.raise_for_status()  # Raise an exception for bad status codes
        return result.content
    except requests.exceptions.RequestException as e:
        print(f"Error generating audio: {e}")
        return None

async def text_to_audio_file(text: str, voice: str = "Brian") -> str:
    """Converts text to an audio file and returns the file path."""
    file_path = r"Data\speech.mp3"

    if os.path.exists(file_path):
        os.remove(file_path)

    audio_content = generate_audio(text, voice)
    if audio_content:
        with open(file_path, "wb") as file:
            file.write(audio_content)
        return file_path
    return ""

def speak(text: str, voice: str = "Brian"):
    """
    Speaks the given text using pygame.
    Handles long text by splitting it and providing a prompt to the user.
    """

    # Responses to prompt user to check the chat screen for further text
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
    ]

    text_parts = str(text).split(".")
    if len(text_parts) > 4 and len(text) > 250:
        chunk = ".".join(text_parts[:2]) + ". " + random.choice(responses)
    else:
        chunk = text

    try:
        pygame.mixer.init()
        audio_file = asyncio.run(text_to_audio_file(chunk, voice))
        if not audio_file:
            print("Could not generate audio file.")
            return

        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except pygame.error as e:
        print(f"Pygame mixer error: {e}")
    finally:
        if pygame.mixer.get_init():
            pygame.mixer.quit()
