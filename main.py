from Frontend.Gui import (
GraphicalUserInterface,
SetAssistantStatus,
ShowTextToScreen,
TempDirectoryPath,
SetMicrophoneStatus,
AnswerModifier,
QueryModifier,
GetMicrophoneStatus,
GetAssistantStatus )
from Backend.Model import FirstLayerDMM
from Backend.RealTimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.Speech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import random
import os
from Backend.Automation import battery_Alert,check_plug

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : hello {Assistantname}, How are you?
{Assistantname} : For you sir! Im always doing well. What use may I be of today?'''
subprocesses= []
Functions = [ "open","close","play","system","content","googlesearch","youtubesearch"]

# chats
def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json','r',encoding= 'utf-8')
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'),'w',encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'),'w',encoding='utf-8') as file:
            file.write(DefaultMessage)

        #chat history    
def ReadChatLogJson():
    with open(r'Data\ChatLog.json','r',encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

#showin gon screen process
def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User",Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant",Assistantname + " ")

    with open (TempDirectoryPath('database.data'),'w',encoding='utf-8')as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsonGui():
    File = open(TempDirectoryPath('Database.data'),"r",encoding='utf-8')
    Data = File.read()
    if len(str(Data))>0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('Responses.data'),"w",encoding='utf-8')
        File.write(result)
        File.close()
def InitalExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsonGui()
InitalExecution()

def MainExecution():
     TaskExecution = False
     ImageExecution = False
     ImageGenerationQuery = ""

     SetAssistantStatus("Listening...")
     Query = SpeechRecognition()
     ShowTextToScreen(f"{Username} : {Query}")
     SetAssistantStatus("Thinking...")
     Decision = FirstLayerDMM(Query)

     print("")
     print(f"Decison : {Decision}")
     print("")

     G = any([i for i in Decision if i.startswith("general")])
     R = any([i for i in Decision if i.startswith("realtime")])

     Merged_query = " and ".join(
         [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
     )

     for queries in Decision:
        if "generate" in queries:
             ImageGenerationQuery = str(queries)
             ImageExecution = True
    
     for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True


     if ImageExecution == True:
         with open(r"Frontend/Files/ImageGeneration.data", "w") as file:
           file.write(f"{ImageGenerationQuery},True")
           print(f"Wrote to file: {ImageGenerationQuery},True")
         try:
           # Use the .venv Python explicitly
           python_path = r"C:\Users\Asus\Desktop\Jarvisxalucard\.venv\Scripts\python.exe"
           script_path = r"C:\Users\Asus\Desktop\Jarvisxalucard\Backend\ImageGeneration.py"
           p1 = subprocess.Popen([python_path, script_path],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE, shell=False)
           subprocesses.append(p1)
           print(f"Subprocess started: PID {p1.pid}")
           out, err = p1.communicate(timeout=5)
           print(f"Subprocess output: {out.decode()}")
           print(f"Subprocess errors: {err.decode()}")
         except Exception as e:
           print(f"Error starting ImageGeneration.py: {e}")


            
     if G and R or R:

        SetAssistantStatus("searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
     else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Query.replace("general","")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime","")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                responses = ["Right away, sir",
                             "Closed Instantly, sir. Is there anything I could assit with sir?",
                             "Alright sir.Please commadn me further",
                             ]
                QueryFinal = random.choice(responses)
                TextToSpeech(Answer)
                SetAssistantStatus("Answering...")
                os._exit(1)
            
def FirstThread():
     while True:
        CurrentStatus = GetMicrophoneStatus()
        
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")
def SecondThread():
    GraphicalUserInterface()
if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread,daemon=True)
    thread2.start()
    SecondThread()
    alert_thread = threading.Thread(target=battery_Alert)
    plug_thread = threading.Thread(target=check_plug)
    
    alert_thread.start()
    plug_thread.start()
    
    alert_thread.join()  # Keeps main thread alive
    plug_thread.join()