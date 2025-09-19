import webbrowser
import pyautogui
import time
from pywhatkit import search, playonyt
from youtube_transcript_api import YouTubeTranscriptApi
import pyperclip as pi
from .tts_utils import speak
from .llm_utils import query_gemini

def GoogleSearch(Topic):
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

def summarize_text(text):
    prompt = f"Summarize the following article: {text}"
    response = query_gemini(prompt)
    speak(response)

def Reader():
    speak("Sure sir, reading your selected data")
    pyautogui.hotkey("ctrl", "c")
    time.sleep(1)
    clipboard_data = pi.paste()
    speak(clipboard_data)

def GetTranscript():
    clipboard_data = ""
    for i in range(5):
        pyautogui.press("f6")
        time.sleep(1)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(1)
        speak("Copied the link, sir. Commencing data analysis")
        clipboard_data = pi.paste()
        if "https://www.youtube.com/watch?" in clipboard_data:
            break
        else:
            time.sleep(1)

    url = clipboard_data.removeprefix("https://www.youtube.com/watch?v=").split("&")[0]
    try:
        transcript = ""
        for i in YouTubeTranscriptApi.get_transcript(url, languages=("en", "hi")):
            transcript += i["text"] + " "
        transcript = transcript.strip()
        summary = summarize_text(transcript)
        speak(summary)
    except:
        speak("Couldn't analyze the data, sir")
