import requests
from AppOpener import give_appnames, open as appopen,close  
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import psutil
import threading
import pyautogui
import wmi
import psutil
import pyaudio
import numpy as np
import time
from scipy.signal import chirp
from youtube_transcript_api import YouTubeTranscriptApi
from keyboard import press,press_and_release
from time import sleep
import os
from pathlib import Path
import google.generativeai as genai 
import feedparser
import win32con
import win32gui
import screen_brightness_control as sbc
import pygame
import requests
import os
import random
import asyncio
import time
from typing import Union
import webbrowser
import google.generativeai as genai
from rich import print
import matplotlib.pyplot as plt
import re
import time
import keyboard
import pyperclip as pi
import random
from os import getcwd
import os
import shutil
import random
from pptx import Presentation
import google.generativeai as genai
import webbrowser
import pyautogui
import time
from youtube_transcript_api import YouTubeTranscriptApi



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
def speak(Text, func=lambda r=None: True, voice="Brian"):
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


# Configure API key
genai.configure(api_key="AIzaSyAKEa9ADDxFSlLrcG7ePCrR4EWiY6FmMpA")

# Load models
flash = genai.GenerativeModel("gemini-pro")

def Gemini(prompt):
    response = flash.generate_content(prompt)
    return response.text

def plot_graph_from_text(text):
    if not text.strip():
        speak("Clipboard is empty. Generating random data instead.")
        plot_random_data()
        return

    prompt = f"Determine the best graph type and extract structured data for plotting from the following data:\n\n{text}"
    structured_data = Gemini(prompt)
    print("[green]Generated Data and Graph Type:", structured_data)
    plot_from_gemini_response(structured_data)

def plot_from_gemini_response(response_text):
    graph_type = ""
    data_dict = {}
    lines = response_text.split("\n")
    
    for i, line in enumerate(lines):
        if "Best Graph Type:" in line:
            graph_type = line.split("Best Graph Type:")[-1].strip().lower()
        elif "|" in line and "---" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) == 2:
                category, value = parts
                value = re.sub(r'[^0-9.]', '', value)
                if value.replace(".", "").isdigit():
                    data_dict[category] = round(float(value), 2)
    
    if not graph_type:
        print("[red]No valid graph type detected. Defaulting to bar chart.")
        graph_type = "bar"

    if not data_dict:
        print("[red]No valid data found. Generating random data instead.")
        plot_random_data()
        return

    if "bar" in graph_type:
        plot_bar_chart(data_dict)
    elif "pie" in graph_type:
        plot_pie_chart(data_dict)
    elif "line" in graph_type:
        plot_line_chart(data_dict)
    elif "scatter" in graph_type:
        plot_scatter_chart(data_dict)
    else:
        print("[red]Invalid graph type specified. Using bar chart as default.")
        plot_bar_chart(data_dict)

def plot_random_data():
    random_data = {f"Category {i+1}": round(random.uniform(10, 100), 2) for i in range(5)}
    graph_types = ["bar", "pie", "line", "scatter"]
    chosen_graph = random.choice(graph_types)
    
    print(f"[blue]Generated Random Graph Type: {chosen_graph}[/blue]")
    print(f"[blue]Generated Random Data: {random_data}[/blue]")

    if chosen_graph == "bar":
        plot_bar_chart(random_data)
    elif chosen_graph == "pie":
        plot_pie_chart(random_data)
    elif chosen_graph == "line":
        plot_line_chart(random_data)
    else:
        plot_scatter_chart(random_data)

def plot_bar_chart(data_dict):
    categories, values = list(data_dict.keys()), list(data_dict.values())
    plt.bar(categories, values, color="skyblue")
    plt.title("Bar Chart")
    plt.xlabel("Categories")
    plt.ylabel("Values")
    plt.xticks(rotation=45)
    plt.show()

def plot_pie_chart(data_dict):
    categories, values = list(data_dict.keys()), list(data_dict.values())
    plt.pie(values, labels=categories, autopct='%1.1f%%', startangle=90)
    plt.title("Pie Chart")
    plt.show()

def plot_line_chart(data_dict):
    categories, values = list(data_dict.keys()), list(data_dict.values())
    plt.plot(categories, values, marker='o')
    plt.title("Line Chart")
    plt.xlabel("Categories")
    plt.ylabel("Values")
    plt.xticks(rotation=45)
    plt.show()

def plot_scatter_chart(data_dict):
    categories, values = list(data_dict.keys()), list(data_dict.values())
    plt.scatter(categories, values, color="red", marker="o")
    plt.title("Scatter Plot")
    plt.xlabel("Categories")
    plt.ylabel("Values")
    plt.xticks(rotation=45)
    plt.show()

def dataExtractor():
    keyboard.press_and_release("ctrl + c")
    time.sleep(1)
    clipboard_data = pi.paste()
    
    if not clipboard_data.strip():
        speak("Clipboard is empty! Switching to random graph generation")
        plot_random_data()
    else:
        speak("[Clipboard data copied. Generating graph.")
        plot_graph_from_text(clipboard_data)

def summarize_text(text):
    prompt = f"Summarize the following article: {text}"
    response = Gemini(prompt)
    speak(response)

def Reader():
    speak("Sure sir, reading your selected data")
    keyboard.press_and_release("ctrl + c")
    time.sleep(1)
    clipboard_data = pi.paste()
    speak(clipboard_data)

def GetTranscript():
    clipboard_data=""
    for i in range(5):
        keyboard.press("f6")
        time.sleep(1)
        keyboard.press_and_release("ctrl + c")
        time.sleep(1)
        speak("Copied the link, sir. Commencing data analysis")
        clipboard_data = pi.paste()
        if "https://www.youtube.com/watch?" in clipboard_data:
            break
        else:
            time.sleep(1)
    
    url= clipboard_data.removeprefix("https://www.youtube.com/watch?v=").split("&")[0]
    try:
        transcript=""
        for i in YouTubeTranscriptApi.get_transcript(url,languages=("en","hi")):
            transcript += i["text"] + " "
        transcript = transcript.strip()
        summary = summarize_text(transcript)
        speak(summary)
    except:
        speak("Couldn't analyze the data, sir")

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")  # Correct key name here

classes = ["Kubwf", "hgKElc", "LTKOO SY7ric", "Z0LcW", "gsrt vk_bk FzvwSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb48b gsrt", "sXLaOe", "LWkFKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "My good sir. your words my ways;Shall serve by any means possible:",
    "At YOUR service!, sir.",
    "right away.. my good sir!",
]

messages = []
SystemChatBot = [{"role": "system", "content": "Hello, I am " + os.environ.get('username', 'user') + ", you are a content writer, you have to write contents like letters, messages to loves ones or professionals that are short and human-like, you might also be asked to write books, songs etc. You obey every command and execute in the most human way possible."}]
 


# Hardcode API key
genai.configure(api_key="AIzaSyAKEa9ADDxFSlLrcG7ePCrR4EWiY6FmMpA")

# Load model
flash = genai.GenerativeModel("gemini-1.5-flash")

def Gemini(prompt):
    """
    Calls Gemini API to generate content based on the prompt.
    """
    try:
        response = flash.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

def createfile(content, text_type, name):                    # creates and saves to desktop
    # Get desktop path
    desktop = Path.home() / "Desktop"                
    
    # Ensure text_type starts with a dot
    if not text_type.startswith('.'):
        text_type = '.' + text_type
    
    # Create full file path
    file_path = desktop / f"{name}{text_type}"
    speak("sir, the file generation process is in progress.")
    try:
        if content.strip() == "":
            # Create empty file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('')
            print(f"Created empty file: {file_path}")
        else:
            # Send text_type in the prompt to determine the output format
            prompt = (
                f"You are Jarvis, an AI assistant. Based on the input '{content}', "
                f"generate raw content for a '{text_type}' file. "
                "For .bat files, use valid Windows CMD commands. "
                "For other file types, generate plain text unless specified otherwise. "
                "Do not include any markdown, code blocks (like ```python or ```), "
                "or external explanations—just the raw content needed for the file."
            )
            generated_content = Gemini(prompt)
            
            # Write AI-generated content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(generated_content)
            print(f"Created file with AI content: {file_path}")
            speak("opening the file, sir")
            os.startfile(file_path)
    except Exception as e:
       print(f"Error creating file: {str(e)}")

'''chrome automation exists here
tab automation
google search'''

def GoogleSearch(Topic):                                   #golululu search
    search(Topic)
    return True

def newtab():
    pyautogui.hotkey('ctrl', 't')

def closetab():
    pyautogui.hotkey('ctrl', 'w')

def zin():
    pyautogui.hotkey('ctrl', '+')

def zout():
    pyautogui.hotkey('ctrl', '-')

def refresh():
    pyautogui.hotkey('ctrl', 'r')

def nexttab():
    pyautogui.hotkey('ctrl', 'tab')

def previoustab():
    pyautogui.hotkey('ctrl', 'shift', 'tab')

def history():
    pyautogui.hotkey('ctrl', 'h')

def bookmarks():
    pyautogui.hotkey('ctrl', 'b')

def fullscreen():
    pyautogui.hotkey('f11')

def inco():
    pyautogui.hotkey('ctrl', 'shift', 'n')    
 
  
''' DONOT ADD ANY CHROME RELATED BS BELOW THE LINE'''


def Content(Topic):                                   # writer ai
    def createfile(content, text_type=None, name=None):  # Default params for flexibility
        # Get desktop path
        desktop = Path.home() / "Desktop"                
        
        # Load Gemini API key and model on function call
        genai.configure(api_key="AIzaSyAKEa9ADDxFSlLrcG7ePCrR4EWiY6FmMpA")
        flash = genai.GenerativeModel("gemini-1.5-flash")
        
        # Maintain original message handling for system compatibility
        messages.append({"role": "user", "content": f"{content}"})
        
        # Strict prompt to ensure clean output
        prompt = (
            f"You are Jarvis, an AI assistant. For the input '{content}', "
            f"generate raw content for an appropriate file type. "
            "If it’s a program (e.g., 'write a calculator program'), output executable code (e.g., Python for .py). "
            "For .bat, use Windows CMD commands. For plain text, use .txt. "
            "Output ONLY the filename with extension (e.g., 'calculator.py') on the first line, "
            "followed by the raw content starting on the second line. "
            "Do NOT include any extra text, labels, comments, or explanations beyond the filename and content."
        )
        try:
            response = flash.generate_content(prompt)
            Answer = response.text
        except Exception as e:
            Answer = f"Gemini API error: {str(e)}"
        
        # Parse the response
        lines = Answer.splitlines()
        if len(lines) > 1 and '.' in lines[0]:
            file_name_with_ext = lines[0].strip()  # First line is 'filename.extension'
            content_to_write = "\n".join(lines[1:]).strip()  # Rest is the content
        else:
            # Fallback with sensible naming
            file_name_with_ext = "generated_file.txt" if "program" not in content.lower() else "generated_program.py"
            content_to_write = Answer
        
        # Extract name and text_type from AI suggestion
        name, text_type = file_name_with_ext.rsplit('.', 1)
        text_type = '.' + text_type
        
        # Create full file path
        file_path = desktop / f"{name}{text_type}"
        speak("sir, the file generation process is in progress.")
        
        try:
            # Append response to messages (keeps system integration)
            messages.append({"role": "assistant", "content": content_to_write})
            
            if content_to_write.strip() == "":
                # Create empty file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('')
                print(f"Created empty file: {file_path}")
            else:
                # Write content directly
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content_to_write)
                print(f"Created file with content: {file_path}")
                speak(f"file saved as {file_name_with_ext} and opening with the default program, sir")
                # Use subprocess to open with the default program
                subprocess.Popen(['start', str(file_path)], shell=True)
            
            return content_to_write  # Return the generated content
        except Exception as e:
            print(f"Error creating file: {str(e)}")
            return None

    # Process the topic and call createfile directly
    Topic = Topic.replace("content", "").strip()
    contentByAI = createfile(Topic)  # Let AI decide type and name
    
    return True

''' Youtube realated queiries are heree
ytseach
playyt
yt command controls'''  

def YoutubeSearch(Topic):          
    url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(url4Search)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True

def seek_backward():
    pyautogui.press('left')

def seek_forward_10s():
    pyautogui.press('l')

def seek_backward_10s():
    pyautogui.press('j')

def seek_backward_frame():
    pyautogui.press(',')

def seek_forward_frame():
    pyautogui.press('.')

def seek_to_beginning():
    pyautogui.press('home')

def seek_to_end():
    pyautogui.press('end')

def seek_to_previous_chapter():
    pyautogui.hotkey('ctrl', 'left')

def seek_to_next_chapter():
    pyautogui.hotkey('ctrl', 'right')

def decrease_playback_speed():
    pyautogui.hotkey('shift', ',')

def increase_playback_speed():
    pyautogui.hotkey('shift', '.')

def move_to_next_video():
    pyautogui.hotkey('shift', 'n')

def move_to_previous_video():
    pyautogui.hotkey('shift', 'p')

'''Yt commands end here
please donot add any code below this line'''


def OpenApp(app):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        speak(f"sir, App {app} not found. Do you want me to Install it?")
        return False


  # close everything expect chrome in taskbar (voicerecognition)


def CloseApp(app): 
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

# below section is for Taskbar automation

                        # to get data

def get_running_apps_windows():
    try:
      
        # Get a list of running processes
      processes = [proc.name() for proc in psutil.process_iter(['name'])]
      return list(set(processes))  # Remove duplicates
    except Exception as e:
       return f"Error: {e}"

def Runningapps(name="Running Apps",text_type="txt"):
   
   speak("since there are a lot. A lot of files running at the moment. Im writing them in the notepad, sir.")
   try: 
        desktop = Path.home() / "Desktop"                
    
    # Ensure text_type starts with a dot
        if not text_type.startswith('.'):
           text_type = '.' + text_type
    
    # Create full file path
        file_path = desktop / f"{name}{text_type}"
        running_apps = get_running_apps_windows()
    
     # Write AI-generated content to file
        with open(file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(running_apps))
        print(f"Created file with AI content: {file_path}")
        os.startfile(file_path)

   except Exception as e:
        print(f"Error creating file: {str(e)}")
   speak("displayed the file. sir")


'''System related code here'''

def system(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def up():
        keyboard.press_and_release("volume up")

    def down():
        keyboard.press_and_release("volume down")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        up()
    elif command == "volume down":
        down()
    return 
  
  
'''Additional power tools previously, now automated'''
 
 #check weather using open-meteo 

def weather(city):
    """
    City to weather using Open-Meteo API
    :param city: City
    :return: weather details

    """
    '''use speak2 for output of huge texts
      use TextToSpeech as speak for normal texts
    '''
    try:
        # Get latitude & longitude
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&format=json"
        geo_response = requests.get(geo_url).json()

        # Debugging the response
        print(geo_response)  # Add this to check what the API returns
        
        if "results" in geo_response:
            location = geo_response["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            elevation = location["elevation"]
            timezone = location["timezone"]
            country = location["country"]
            city_name = location["name"]

            # Get weather data
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_response = requests.get(weather_url).json()

            if "current_weather" in weather_response:
                data = weather_response["current_weather"]
                temp = data["temperature"]
                wind_speed = data["windspeed"]
                weather_code = data["weathercode"]  # Weather condition code

                # Weather condition mapping
                weather_conditions = {
                    0: "Clear sky",
                    1: "Mainly clear",
                    2: "Partly cloudy",
                    3: "Overcast",
                    45: "Fog",
                    48: "Depositing rime fog",
                    51: "Drizzle (light)",
                    53: "Drizzle (moderate)",
                    55: "Drizzle (dense)",
                    61: "Rain (light)",
                    63: "Rain (moderate)",
                    65: "Rain (heavy)",
                    71: "Snow (light)",
                    73: "Snow (moderate)",
                    75: "Snow (heavy)",
                    80: "Rain showers (light)",
                    81: "Rain showers (moderate)",
                    82: "Rain showers (violent)",
                    95: "Thunderstorm",
                    96: "Thunderstorm with light hail",
                    99: "Thunderstorm with heavy hail",
                }

                weather_desc = weather_conditions.get(weather_code, " Having Unknown weather condition") #if error code

                final_response = f"""
                Good day Sir! here's the latest weather update for you.

                The city of {city_name}, located in {country}, above {elevation} meters above sea level,falls under the {timezone} timezone. 
                Currently, the weather in {city_name} is {weather_desc}. The temperature is {temp}°C, with a wind speed of {wind_speed} km/h. 

                Be aware of the weather, plan accordingly, and stay safe. Enjoy your day!
                """
                speak2(final_response) 

#uses speak2 fucntion donot call TTS

            else:
                speak2("Sorry Sir, I couldn't retrieve the weather data.")
        else:
            speak2("Sorry Sir, I couldn't find the city in my database. Please try again.")
    
    except Exception as e:
        speak2(f"An error occurred: {str(e)}")
 

 #System specific statistics

def systemstats():
    speak("calculations in progress")
    cpu_stats = str(psutil.cpu_percent())
    battery_percent = psutil.sensors_battery().percent
    memory_in_use = psutil.virtual_memory().used / (1024 ** 3)  # Convert to GB
    total_memory = psutil.virtual_memory().total / (1024 ** 3)  # Convert to GB
    final_res = f"Currently {cpu_stats} percent of CPU, {memory_in_use:.2f} GB of RAM out of total {total_memory:.2f} GB is being used. and the battery level is at {battery_percent} percent"
    print(final_res)
    speak(final_res)

#get news no api required

def news():
    """Fetch and speak news with stock market updates using speak2"""
    # General news from Times of India
    toi_rss_url = "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    toi_feed = feedparser.parse(toi_rss_url)
    
    # Stock market news from Economic Times
    et_rss_url = "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms"
    et_feed = feedparser.parse(et_rss_url)
    
    # Check if either feed has entries
    if not toi_feed.entries and not et_feed.entries:
        news_text = "The news is that there are no updates available right now "
        speak2(news_text)
        print(news_text)
        return
    
    # Build a structured news string
    news_text = "Good day! Here's your quick news update from India. "
    
    # Add general news (limit to 2 for brevity)
    if toi_feed.entries:
        news_text += "Top stories from The Times of India: "
        for i, entry in enumerate(toi_feed.entries[:2], 1):
            title = entry.get("title", "an event occurred")
            news_text += f"{i}. {title}. "
    else:
        news_text += "No general news updates available at the moment. "
    
    # Add stock market news (limit to 1 for brevity)
    if et_feed.entries:
        stock_title = et_feed.entries[0].get("title", "market movement reported")
        news_text += f"In stock market news from The Economic Times: {stock_title}. "
    else:
        news_text += "No stock market updates available currently. "
    
    # Closing
    news_text += "That’s your news summary for now!"
    
    print(news_text)   #use print before speak2 as it causes win32 error
    speak2(news_text)


#Internet connection chcker
 
def isOnline(url="https://www.google.com", timeout=5):
 
    try:
        response = requests.get(url, timeout=timeout)
        status_code = response.status_code
        
        if 200 <= status_code < 300:
            speak("Your internet is working optimally, sir.")
        else:
            speak(f"Internet check returned status code {status_code}, sir. It might not be working as expected.")

            
    except requests.ConnectionError:
        speak("Internet is currently down, sir. No connection could be established.")
    except requests.Timeout:
        speak("Internet check timed out, sir. The connection is too slow or unavailable.") #inapplicable
    except requests.RequestException as e:
        speak(f"An error occurred while checking the internet, sir. Details: {str(e)}")

''' Uses  check_plug fucntion using loops '''


#note: use threading to run functions indefinately in main.py


def battery_Alert():
    while True:
        battery = psutil.sensors_battery()
        if battery is None:
            speak("Sir, I couldn't detect a battery on this device.")
            break
        percentage = int(battery.percent)
        if percentage == 100:
            speak(f"Sir, the battery is fully charged at {percentage} percent. Do you need any further assistance?")
        elif percentage <= 5:
            speak(f"Sir, critical alert! The battery is at {percentage} percent. You're doomed lmao")
        elif percentage <= 10:
            speak(f"Sir, urgent warning! The battery is at {percentage} percent. Please plug in now!")
        elif percentage <= 20:
            speak(f"Sir, the battery is at {percentage} percent. Consider charging the device soon.")
        time.sleep(1200)

def check_plug():
    """Instantly detect charger plug/unplug and speak/print once per state change (Windows only)"""
    print("_____started___")
    battery = psutil.sensors_battery()
    if battery is None:
        print("Sir, no battery detected to monitor charging status.")
        speak("Sir, no battery detected to monitor charging status.")
        return
    
    # Initial state
    previous_state = battery.power_plugged
    has_reported = False  # Flag to prevent repeated output in the same state
    
    def wnd_proc(hwnd, msg, wparam, lparam):
        nonlocal previous_state, has_reported
        if msg == win32con.WM_POWERBROADCAST and wparam == win32con.PBT_APMPOWERSTATUSCHANGE:
            battery = psutil.sensors_battery()
            current_state = battery.power_plugged
            
            # Only report if state changes and hasn’t been reported yet
            if current_state != previous_state:
                if current_state:  # Charger plugged in
                    print("Sir, the charger has been plugged in.")
                    speak("Sir, the charger has been plugged in.")
                else:  # Charger unplugged
                    print("Sir, the charger has been unplugged.")
                    speak("Sir, the charger has been unplugged.")
                previous_state = current_state
                has_reported = True  # Mark as reported
            elif has_reported:
                has_reported = False  # Reset when state stabilizes for next change
        
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    # Register and create the window
    wc = win32gui.WNDCLASS()
    wc.lpszClassName = "PowerMonitor"
    wc.lpfnWndProc = wnd_proc
    win32gui.RegisterClass(wc)

    hwnd = win32gui.CreateWindow(
        wc.lpszClassName,
        "Power Monitor Window",
        0, 0, 0, 0, 0, 0, 0, None, None
    )

    win32gui.PumpMessages()

def check_percentage():
    """Check and return the current battery percentage"""
    battery = psutil.sensors_battery()
    if battery is None:
        speak("Sir, no battery detected on this device.")
        return None
    
    percent = int(battery.percent)
    speak(f"Sir, the current battery level is {percent} percent.")
    return percent

#Brightness controls

def get_brightness_windows():  # donot call
    try:
        w = wmi.WMI(namespace='wmi')
        brightness_methods = w.WmiMonitorBrightness()
        brightness_percentage = brightness_methods[0].CurrentBrightness
        return brightness_percentage
    except Exception as e:
        return f"Error: {e}"

def br():  #callable uses the non callable
    brightness = get_brightness_windows()
    speak(f"The Current Brightness is {brightness}%,Do you want me Increase, or Decrease the brightness levels; for you. sir?")

# use win32 if sbc doesnt woek

#increase (brightness is input)
def increasebr(brightness):
    sbc.set_brightness(brightness)
    speak("The brightness has been set to {brightness}%")    

    #decrease
def decreasebr(brightness):

    sbc.set_brightness(brightness)
    speak("The brightness has been set to {brightness}%")    


# microphone shi here 
                                                        #read instr
'''Only callable funtion:
michealth()'''


def get_mic_health(seconds=5, initial_threshold=500):
    speak(" getting microphone acces ")
    CHUNK = 1024  # Audio chunk size
    FORMAT = pyaudio.paInt16  # 16-bit resolution
    CHANNELS = 1  # Mono audio
    RATE = 44100  # Sampling rate

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open the stream
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    speak(f"Recording for {seconds} seconds...")
    time.sleep(1)  # Small pause before recording

    # Initialize variables
    sound_count = 0
    total_samples = 0
    noise_floor = 0  # Ambient noise level
    clipping_count = 0
    signal_sum = 0  # Sum of sound levels
    noise_sum = 0  # Sum of background noise levels (below threshold)
    freq_analysis = []  # Frequency analysis data

    for _ in range(0, int(RATE / CHUNK * seconds)):
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        volume = np.linalg.norm(data)
        
        # Frequency analysis (FFT)
        freqs = np.fft.fftfreq(len(data))
        fft_spectrum = np.abs(np.fft.fft(data))
        freq_analysis.append(fft_spectrum)

        # Update ambient noise level dynamically
        noise_floor = max(noise_floor, np.mean(np.abs(data)) * 1.5)

        # Dynamic threshold based on ambient noise
        dynamic_threshold = max(initial_threshold, noise_floor)

        # Check for sound detection
        if volume > dynamic_threshold:  # Sound detected
            sound_count += 1
            signal_sum += volume
        else:  # No sound detected (background noise)
            noise_sum += volume

        # Detect clipping (when the sound is too loud for the mic)
        if np.max(np.abs(data)) >= 32767:
            clipping_count += 1

        total_samples += 1

    # Calculate metrics
    mic_health = (sound_count / total_samples) * 100
    avg_signal = signal_sum / max(1, sound_count)
    avg_noise = noise_sum / max(1, (total_samples - sound_count))
    snr = 10 * np.log10(avg_signal / max(1, avg_noise))  # Signal-to-Noise Ratio
    avg_clipping = (clipping_count / total_samples) * 100

    # Frequency analysis (average frequencies captured)
    avg_fft_spectrum = np.mean(freq_analysis, axis=0)
    freq_range_coverage = np.mean(avg_fft_spectrum > np.median(avg_fft_spectrum)) * 100

    # Close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    speak("samples recorded sir. Now i shall dectate the results one by one")
    # Output advanced health metrics
    health_report = f'''Microphone Health (%): {mic_health},
        Average Signal to Noise Ratio (dB): {snr},
        Clipping Percentage (%): {avg_clipping},
        Frequency Range Coverage (%): {freq_range_coverage}'''

    return health_report

#Use string not sets or loop

def michealth():
    health_metrics = get_mic_health(seconds=5)
 
    print(health_metrics)
  


# speaker ahi here

'''The only callable fucntion in the mode:
speakerhalth()'''



def play_tone(frequency, duration=2, volume=0.5, sample_rate=44100):
    """
    Plays a single tone of a specific frequency through the speaker.
    """
    # Generate samples for the sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(frequency * t * 2 * np.pi)

    # Ensure the tone is in the correct format
    audio_data = (tone * volume * 32767).astype(np.int16)

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    output=True)

    # Play the tone
    stream.write(audio_data.tobytes())

    # Stop the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

def play_sweep(duration=5, volume=0.5, sample_rate=44100, start_freq=20, end_freq=20000):
    """
    Plays a frequency sweep from start_freq to end_freq through the speaker.
    Useful for testing the full frequency range of the speaker.
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sweep = chirp(t, start_freq, t[-1], end_freq, method='logarithmic')

    # Ensure the sweep is in the correct format
    audio_data = (sweep * volume * 32767).astype(np.int16)

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    output=True)

    # Play the sweep
    stream.write(audio_data.tobytes())

    # Stop the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

def speakertest():
    """
    This function plays different tones and sweeps to test the speaker's health.
    It returns a speaker health percentage based on the tone coverage.
    """
    speak("Playing test tones...")
    health_score = 0

    # Test low-frequency tones (below 500 Hz)
    speak("100 Hz tone...")
    play_tone(100, duration=2)
    time.sleep(1)
    health_score += 25  # Assuming low-frequency played fine

    # Test mid-frequency tones (500 Hz to 5000 Hz)
    speak(" 1000 Hz tone...")
    play_tone(1000, duration=2)
    time.sleep(1)
      # Assuming mid-frequency played fine

    # Test higher frequencies (5000 Hz and above)
    speak("5000 Hz tone...")
    play_tone(5000, duration=2)
    time.sleep(1)
    health_score += 20  # Slightly lower score for high frequencies, which may be harder for some speakers

    speak(" 10,000 Hz tone...")
    play_tone(10000, duration=2)
    time.sleep(1)
    health_score += 15  # High-pitch tones are harder to reproduce

    # Play a frequency sweep to test full frequency response
    speak("Playing frequency sweep from 20 Hz to 20,000 Hz...")
    play_sweep(duration=5)
    time.sleep(1)
    health_score += 15  # Frequency sweep covers a wide range

    # Speaker health assessment
    speak("\nSpeaker health test complete.")

    # Calculate health percentage
    speak(f"\nSpeaker Health: {health_score}%")
    print(f"\nSpeaker Health: {health_score}%")
    if health_score == 100:
        speak("The speaker is in excellent condition!")
    elif 80 <= health_score < 100:
        speak("The speaker is in good condition.")
    elif 60 <= health_score < 80:
        speak("The speaker is in average condition.")
    else:
        speak("The speaker might be in poor condition.")


#random features, troll memes

# advice feature
def advice():
    def get_advice():
       res = requests.get("https://api.adviceslip.com/advice").json()
       return res['slip']['advice']
    advice_generated = get_advice()
    speak(advice_generated)

def joke():
    def get_joke():
            headers = {
                 'Accept': 'application/json'
            }
            res = requests.get("https://icanhazdadjoke.com/", headers=headers).json()
            return res["joke"]
    joke_generated = get_joke()
    speak(joke_generated)


async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        if command.startswith("open "):
            if "open it" in command:
                pass
            if "open file" in command:
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)
        elif command.startswith("general "):
            pass
        elif command.startswith("realtime"):
            pass
        elif command.startswith("Close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)
        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
        elif command.startswith("googlesearch"):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("googlesearch"))
            funcs.append(fun)
        elif command.startswith("youtubesearch"):
            fun = asyncio.to_thread(YoutubeSearch, command.removeprefix("youtubesearch "))
            funcs.append(fun)
        elif command.startswith("system "):
            fun = asyncio.to_thread(system, command.removeprefix("system "))
            funcs.append(fun)
        else:
            print(f"No Functions found for {command}")
    
    results = await asyncio.gather(*funcs)
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True
