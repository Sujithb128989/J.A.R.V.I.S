import os
from time import sleep
from datetime import datetime
import json
import pyaudio
import numpy as np
from scipy.signal import chirp
from .tts_utils import speak
from groq import Groq
from dotenv import load_dotenv
import threading

load_dotenv()

# Initialize client
GroqAPIKey = os.getenv("GroqAPIKey")
client = None
if GroqAPIKey:
    client = Groq(api_key=GroqAPIKey)
else:
    print("Warning: GroqAPIKey not found in .env file. Alarm setting will not work.")

def play_chirp():
    t = np.linspace(0, 5, 44100 * 5)
    audio = (chirp(t, 20, t[-1], 2000) * 0.5 * 32767).astype(np.int16)  # 20 Hz to 2000 Hz
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
    stream.write(audio.tobytes())
    stream.close()
    p.terminate()

ALARM_FILE = os.path.join("Frontend", "Files", "AlarmData.json")

def add_alarm(text):
    if not client:
        speak("The alarm service is not configured. Please set the GroqAPIKey in the .env file.")
        return

    prompt = f"Parse '{text}' to JSON: {{'activity': str, 'time': 'YYYY-MM-DD HH:MM', 'triggered': False}}. Current date: {datetime.now().strftime('%Y-%m-%d')}"
    try:
        resp = client.chat.completions.create(model="mixtral-8x7b-32768", messages=[{"role": "user", "content": prompt}]).choices[0].message.content
        # Extract JSON from response (assuming it’s wrapped or has extra text)
        json_start = resp.find('{')
        json_end = resp.rfind('}') + 1
        json_str = resp[json_start:json_end]
        alarm = json.loads(json_str)
        alarms = json.load(open(ALARM_FILE, "r")) if os.path.exists(ALARM_FILE) else []
        alarms.append(alarm)
        with open(ALARM_FILE, "w") as f:
            json.dump(alarms, f)
        speak(f"Okay sir, reminder set for {alarm['activity']} at {alarm['time']}.")
    except Exception as e:
        speak("Failed to set reminder, sir.")
        print(f"Error: {e} - Response: {resp}")

def check_alarms():
    if not os.path.exists(ALARM_FILE):
        return False, [], []
    with open(ALARM_FILE, "r") as f:
        alarms = json.load(f)
    now = datetime.now()
    active, triggered = [], []
    for a in alarms:
        t = datetime.strptime(a["time"], "%Y-%m-%d %H:%M")
        if not a["triggered"] and now >= t:
            a["triggered"] = True
            triggered.append(a)
        elif not a["triggered"]:
            active.append(a)
    return bool(triggered), active, triggered

def AlarmProgram():
    speak("Reminder system online, sir.")
    while True:
        trigger, active, triggered = check_alarms()
        if trigger:
            for a in triggered:
                play_chirp()
                speak(f"Sir, you might have forgotten about {a['activity']}.")
            with open(ALARM_FILE, "w") as f:
                json.dump(active, f)
        sleep(5)  # Check every 5 seconds

def run_alarm():
    AlarmProgram()

if __name__ == "__main__":
    add_alarm("end assignment in 2 minutes")  # Your example
    alarm_thread = threading.Thread(target=run_alarm, daemon=True)
    alarm_thread.start()
    while True:
        sleep(1)
