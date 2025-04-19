import pygame
import requests
import os
import random
import asyncio
import time
from typing import Union

def generate_audio(message: str, voice: str = "Brian") -> Union[None, str]:
    url: str = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={{{message}}}"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

    try:
        result = requests.get(url=url, headers=headers)
        return result.content
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

async def TextToAudioFile(text: str, voice: str = "Brian") -> None:
    file_path = r"Data\speech.mp3"

    # Remove existing file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate audio using StreamElements TTS API
    audio_content = generate_audio(text, voice)
    if audio_content:
        with open(file_path, "wb") as file:
            file.write(audio_content)

# Function to play speech with pygame
def TTS(Text, func=lambda r=None: True, voice="Brian"):
    try:
        pygame.mixer.init()  # Ensure pygame mixer is initialized at the beginning
        while True:
            try:
                # Convert text to audio and save it
                asyncio.run(TextToAudioFile(Text, voice))

                # Load the saved speech file
                pygame.mixer.music.load(r"Data\speech.mp3")  # Correct file name
                pygame.mixer.music.play()

                # Keep checking if the music is playing and if func() is still true
                while pygame.mixer.music.get_busy():
                    if func() == False:
                        break
                    pygame.time.Clock().tick(10)
                return True
            except Exception as e:
                print(f"Error in TTS: {e}")
                exit()
            finally:
                try:
                    func(False)
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()
                except Exception as e:
                    print(f"Error in finally block: {e}")
                    exit()
    except pygame.error as e:
        print(f"Pygame mixer error: {e}")
        return False
def speak2(Text, voice="Brian", stop_flag=lambda: False):
    
    try:
        pygame.mixer.init()
        while not stop_flag():
            try:
                # Generate and save audio
                asyncio.run(TextToAudioFile(Text, voice))
                
                # Load and play
                pygame.mixer.music.load(r"Data\speech.mp3")
                pygame.mixer.music.play()
                
                # Wait while playing, checking stop condition
                while pygame.mixer.music.get_busy():
                    if stop_flag():
                        break
                    pygame.time.Clock().tick(10)
                
                time.sleep(0.5)  # Small pause between repetitions
                
            except Exception as e:
                print(f"Error in speak2: {e}")
                exit() 
                
    except pygame.error as e:
        print(f"Pygame mixer error in speak2: {e}")
        exit()
    finally:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in speak2 cleanup: {e}")
            exit()

# Text to Speech with additional logic
def TextToSpeech(Text, func=lambda r=None: True, voice="Brian"):
    # Split the text by period to manage longer texts
    Data = str(Text).split(".")

    # Responses to prompt user to check the chat screen for further text
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    # Handle long texts that need to be split into chunks
    if len(Data) > 4 and len(Text) > 250:
        chunk = ".".join(Data[:2])  # Use a chunk of the first few parts
        TTS(chunk + ". " + random.choice(responses), func, voice)
    else:
        TTS(Text, func, voice)

# Main execution
if __name__ == "__main__":
    while True:
        Text = input("Enter the text: ")
        TextToSpeech(Text)