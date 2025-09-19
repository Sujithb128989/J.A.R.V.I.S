import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv
import os
from time import sleep
from Speech import TextToSpeech as speak

load_dotenv()

def open_images(prompt):
    speak("displaying images,sir")
    folder_path = r"Frontend\Files\Generated Images"
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            print(f"Image exists: {os.path.exists(image_path)}")
            os.startfile(image_path)  # Windows-specific
            sleep(1)
        except Exception as e:
            print(f"Failed to open {image_path}: {e}")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
if not HUGGINGFACE_API_KEY:
    speak("Hugging Face API key is not configured. Please set it in the .env file.")
    # Exit or handle the absence of the key gracefully
    exit()

headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

async def Query(payload):
    print(f"Sending API request with payload: {payload}")
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

async def generate_images(prompt: str):
    tasks = []
    for _ in range(4):
        payload = {"inputs": f"{prompt}, quality=4k, ultra High details, deep={randint(0, 1000000)}"}
        task = asyncio.create_task(Query(payload))
        tasks.append(task)
    image_bytes_list = await asyncio.gather(*tasks)
    folder_path = r"Frontend\Files\Generated Images"
    for i, image_bytes in enumerate(image_bytes_list):
        file_path = os.path.join(folder_path, f"{prompt.replace(' ', '_')}{i + 1}.jpg")
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        print(f"Saved image: {file_path}")

def GenerateImages(prompt: str):
    # Create folder if it doesn’t exist
    folder_path = r"Frontend\Files\Generated Images"
    os.makedirs(folder_path, exist_ok=True)
    # Delete past files
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted old file: {file_path}")
    speak(f"Generating images for: {prompt}")
    asyncio.run(generate_images(prompt))
    open_images(prompt)

while True:
    try:
        with open(r"Frontend\Files\Imagegeneration.data", "r") as f:
            Data: str = f.read()
            print(f"Read from file: {Data}")

        Prompt, status = Data.split(",")


        if status == "True":
            print("Generating Images...")
            GenerateImages(prompt=Prompt)
            with open(r"Frontend\Files\Imagegeneration.data", "w") as f:
                f.write("False,False")

            break
        else:
            sleep(1)
    except :
        pass
