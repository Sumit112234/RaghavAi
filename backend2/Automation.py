from AppOpener import close, open as aapopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import requests
import os
import webbrowser
import subprocess
import asyncio
import keyboard
from typing import List

env_vars = dotenv_values(".env")

# groqApi = env_vars.get("groqKey")
groqApi = os.getenv('groqKey')  

print("hello ji")
classes = []

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
client = Groq(api_key=groqApi)

messages = []

SystemChatBot = [{'role': 'system', 'message': 'Hello, I am your assistant, how can I help you today?'}]

def GoogleSearch(topic):
    search(topic)
    return True

def Content(topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriteAi(prompt):
        messages.append({'role': 'user', 'message': prompt})    

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32786",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content        

        Answer = Answer.replace("</s>", "")
        messages.append({'role': 'system', 'message': Answer})  
        return Answer
    
    topic = topic.replace("Content", "")
    ContentByAi = ContentWriteAi(topic)

    file_path = rf"data\{topic}.txt"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding='utf-8') as f:
        f.write(ContentByAi)

    OpenNotepad(file_path)
    return True 

def YouTubeSearch(topic):
    url = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url)
    return True

def PlayYouTube(topic):
    playonyt(topic)
    return True

def OpenApp(app, sess=requests.Session()):
    try:
        aapopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link['href'] for link in links]

        def search_google(topic):
            url = f"https://www.google.com/search?q={topic}"
            headers = {'User-Agent': useragent}
            response = sess.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.text
            else:
                print("Error:", response.status_code)  
                return None
        
        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])

        return True
    
# OpenApp("task manager")
# PlayYouTube("code with harry")


def CloseApp(app):
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        return False

# CloseApp("task manager")

def System(command):
    def mute():
        keyboard.press_and_release("volume mute")
    def unmute():
        keyboard.press_and_release("volume mute")
    def volume_up():
        keyboard.press_and_release("volume up")
    def volume_down():
        keyboard.press_and_release("volume down")
    
    actions = {
        'mute': mute,
        'unmute': unmute,
        'volume up': volume_up,
        'volume down': volume_down
    }

    if command in actions:
        actions[command]()
    else:
        print("Unknown command")
    
    return True

# System('volume down')


async def translateAndExecute(commands: List[str]):
    funcs = []

    for command in commands:
        if command.startswith("open "):
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
            funcs.append(fun)
        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)
        elif command.startswith("search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("search "))
            funcs.append(fun)
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("search "))
            funcs.append(fun)
        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
        elif command.startswith("youtube "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube "))
            funcs.append(fun)
        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play "))
            funcs.append(fun)
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
        else:
            print("No command found")

    results = await asyncio.gather(*funcs)
    
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

async def AutomationTask(commands: List[str]):
    async for result in translateAndExecute(commands):
        pass
    return True

async def task():
    await AutomationTask(["open task manager", "open file explorar", "search python", "content python", "youtube code with harry", "play python", "system volume down"])
        
if __name__ == "__main__" :
    asyncio.run(task())         
     