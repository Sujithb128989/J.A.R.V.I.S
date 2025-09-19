import os
import random
import shutil
import subprocess
import time
from os import getcwd
from pathlib import Path

import matplotlib.pyplot as plt
import pyperclip as pi
import requests
from AppOpener import close, open as appopen
from pptx import Presentation

from .llm_utils import query_gemini
from .tts_utils import speak


def plot_graph_from_text(text):
    if not text.strip():
        speak("Clipboard is empty. Generating random data instead.")
        plot_random_data()
        return

    prompt = f"Determine the best graph type and extract structured data for plotting from the following data:\n\n{text}"
    structured_data = query_gemini(prompt)
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
    pyautogui.hotkey("ctrl", "c")
    time.sleep(1)
    clipboard_data = pi.paste()

    if not clipboard_data.strip():
        speak("Clipboard is empty! Switching to random graph generation")
        plot_random_data()
    else:
        speak("[Clipboard data copied. Generating graph.")
        plot_graph_from_text(clipboard_data)


def Content(Topic):
    def createfile(content, text_type=None, name=None):
        desktop = Path.home() / "Desktop"

        prompt = (
            f"You are Jarvis, an AI assistant. For the input '{content}', "
            f"generate raw content for an appropriate file type. "
            "If it’s a program (e.g., 'write a calculator program'), output executable code (e.g., Python for .py). "
            "For .bat, use Windows CMD commands. For plain text, use .txt. "
            "Output ONLY the filename with extension (e.g., 'calculator.py') on the first line, "
            "followed by the raw content starting on the second line. "
            "Do NOT include any extra text, labels, comments, or explanations beyond the filename and content."
        )
        Answer = query_gemini(prompt)

        lines = Answer.splitlines()
        if len(lines) > 1 and '.' in lines[0]:
            file_name_with_ext = lines[0].strip()
            content_to_write = "\n".join(lines[1:]).strip()
        else:
            file_name_with_ext = "generated_file.txt" if "program" not in content.lower() else "generated_program.py"
            content_to_write = Answer

        name, text_type = file_name_with_ext.rsplit('.', 1)
        text_type = '.' + text_type

        file_path = desktop / f"{name}{text_type}"
        speak("sir, the file generation process is in progress.")

        try:
            if content_to_write.strip() == "":
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('')
                print(f"Created empty file: {file_path}")
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content_to_write)
                print(f"Created file with content: {file_path}")
                speak(f"file saved as {file_name_with_ext} and opening with the default program, sir")
                subprocess.Popen(['start', str(file_path)], shell=True)

            return content_to_write
        except Exception as e:
            print(f"Error creating file: {str(e)}")
            return None

    Topic = Topic.replace("content", "").strip()
    contentByAI = createfile(Topic)

    return True


def OpenApp(app):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        speak(f"sir, App {app} not found. Do you want me to Install it?")
        return False


def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False


def get_running_apps_windows():
    try:
        processes = [proc.name() for proc in psutil.process_iter(['name'])]
        return list(set(processes))
    except Exception as e:
        return f"Error: {e}"


def Runningapps(name="Running Apps", text_type="txt"):
    speak("since there are a lot. A lot of files running at the moment. Im writing them in the notepad, sir.")
    try:
        desktop = Path.home() / "Desktop"
        if not text_type.startswith('.'):
            text_type = '.' + text_type

        file_path = desktop / f"{name}{text_type}"
        running_apps = get_running_apps_windows()

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(running_apps))
        print(f"Created file with AI content: {file_path}")
        os.startfile(file_path)

    except Exception as e:
        print(f"Error creating file: {str(e)}")
    speak("displayed the file. sir")


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
