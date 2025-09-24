import os
import sys
import time
import mtranslate as mt
from langdetect import detect
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
INPUT_LANGUAGE = os.getenv("InputLanguage", "en-US")
CURRENT_DIR = os.getcwd()
DATA_PATH = os.path.join(CURRENT_DIR, "Data", "Voice.html")
TEMP_DIR_PATH = os.path.join(CURRENT_DIR, "Frontend", "Files")

# --- HTML for Web Speech API ---
HTML_CODE = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start</button>
    <button id="end" onclick="stopRecognition()">Stop</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {{
            recognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
            recognition.lang = '{INPUT_LANGUAGE}';
            recognition.continuous = true;
            recognition.interimResults = true;

            recognition.onresult = function(event) {{
                let final_transcript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {{
                    if (event.results[i].isFinal) {{
                        final_transcript += event.results[i][0].transcript;
                    }}
                }}
                if (final_transcript) {{
                    output.textContent = final_transcript;
                }}
            }};

            recognition.onerror = function(event) {{
                console.error("Speech recognition error", event.error);
            }};

            recognition.onend = function() {{
                // The loop in the Python script will handle restart.
            }};

            recognition.start();
        }}

        function stopRecognition() {{
            if (recognition) {{
                recognition.stop();
            }}
        }}
    </script>
</body>
</html>
'''

with open(DATA_PATH, "w") as f:
    f.write(HTML_CODE)

# --- Selenium WebDriver Setup ---
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36')
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--auto-grant-media-stream")

    # This is crucial for headless mode to access the microphone
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1
    })

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Failed to initialize Chrome WebDriver: {e}")
        return None

# --- Helper Functions ---
def set_assistant_status(status):
    status_file = os.path.join(TEMP_DIR_PATH, "Status.data")
    with open(status_file, "w", encoding='utf-8') as file:
        file.write(status)

def query_modifier(query):
    new_query = query.lower().strip()
    # Basic punctuation, can be improved if needed
    if new_query and new_query[-1] not in ['.', '?', '!']:
        new_query += "."
    return new_query.capitalize()

def universal_translator(text):
    try:
        detected_language = detect(text)
        if detected_language == "en":
            return text
        return mt.translate(text, "en", detected_language)
    except Exception as e:
        print(f"Translation error: {e}")
        return text # Fallback to original text

# --- Main Speech Recognition Logic ---
def SpeechRecognition():
    driver = setup_driver()
    if not driver:
        return "WebDriver initialization failed."

    driver.get("file:///" + DATA_PATH)
    time.sleep(1) # Wait for page to load

    try:
        driver.find_element(by=By.ID, value="start").click()
    except Exception as e:
        print(f"Could not click start button: {e}")
        driver.quit()
        return "Error starting recognition."

    last_text = ""
    while True:
        try:
            current_text = driver.find_element(by=By.ID, value="output").text
            if current_text and current_text != last_text:
                last_text = current_text
                set_assistant_status("Translating...")
                translated_text = universal_translator(last_text)
                final_text = query_modifier(translated_text)

                driver.find_element(by=By.ID, value="end").click()
                driver.quit()
                return final_text

            time.sleep(0.5)

        except Exception as e:
            # This will catch errors if the browser closes or the element is not found
            print(f"Error during speech recognition loop: {e}")
            driver.quit()
            return "An error occurred during recognition."

if __name__ == "__main__":
    print("Starting speech recognition test...")
    recognized_text = SpeechRecognition()
    print(f"Recognized Text: {recognized_text}")