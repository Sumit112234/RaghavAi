import os
import webbrowser
import subprocess
import asyncio
import platform
import requests
import keyboard
from typing import List
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
# from pywhatkit import search, playonyt
import pywhatkit
import platform

if os.environ.get("DISPLAY"):
    try:
        import pyautogui
        import mouseinfo
    except ImportError:
        pyautogui = None
        mouseinfo = None
else:
    pyautogui = None
    mouseinfo = None

try:
    from AppOpener import close, open as aapopen
except ImportError:
    aapopen = None
    close = None

try:
    from groq import Groq
except ImportError:
    Groq = None

env_vars = dotenv_values(".env")
groqApi = os.getenv('groqKey')

if Groq:
    client = Groq(api_key=groqApi)
    messages = []
    SystemChatBot = [{'role': 'system', 'message': 'Hello, I am your assistant, how can I help you today?'}]

useragent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
             "AppleWebKit/537.36 (KHTML, like Gecko) "
             "Chrome/58.0.3029.110 Safari/537.3")

def GoogleSearch(topic):
    pywhatkit.search(topic)
    return True

def playonyt(query):
    if os.environ.get("DISPLAY") is None:  # Prevents running in headless mode
        print("Cannot play YouTube in headless mode")
        return False
    pywhatkit.playonyt(query)
    return True

def OpenApp(app):
    if aapopen:
        try:
            aapopen(app, match_closest=True, output=True, throw_error=True)
            return True
        except Exception:
            pass
    
    system_platform = platform.system().lower()
    try:
        if system_platform == "windows":
            subprocess.run(["start", "", app], shell=True)
        elif system_platform == "darwin":
            subprocess.run(["open", "-a", app])
        elif system_platform == "linux":
            subprocess.run(["xdg-open", app])
        return True
    except Exception as e:
        print(f"Failed to open {app}: {e}")
        return False

def CloseApp(app):
    if close:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except Exception:
            pass
    print("Close app function is not available.")
    return False


def System(command):
    if pyautogui is None:
        print("System command cannot be executed in a headless environment")
        return False

    actions = {
        'mute': lambda: pyautogui.press("volumemute"),
        'unmute': lambda: pyautogui.press("volumemute"),
        'volume up': lambda: pyautogui.press("volumeup"),
        'volume down': lambda: pyautogui.press("volumedown"),
    }

    if command in actions:
        actions[command]()
        return True
    else:
        print("Unknown command")
        return False
    
# def System(command):
#     actions = {
#         'mute': lambda: keyboard.press_and_release("volume mute"),
#         'unmute': lambda: keyboard.press_and_release("volume mute"),
#         'volume up': lambda: keyboard.press_and_release("volume up"),
#         'volume down': lambda: keyboard.press_and_release("volume down"),
#     }
#     actions.get(command, lambda: print("Unknown command"))()
#     return True

async def translateAndExecute(commands: List[str]):
    funcs = []
    for command in commands:
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))
        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))
        elif command.startswith("search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("search ")))
        elif command.startswith("youtube "):
            funcs.append(asyncio.to_thread(lambda: webbrowser.open(f"https://www.youtube.com/results?search_query={command.removeprefix('youtube ')}")))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(playonyt, command.removeprefix("play ")))
        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))
        else:
            print("No command found")
    
    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def AutomationTask(commands: List[str]):
    async for _ in translateAndExecute(commands):
        pass
    return True

async def task():
    await AutomationTask(["open task manager", "open file explorer", "system volume down"])

if __name__ == "__main__":
    asyncio.run(task())


# from AppOpener import close, open as aapopen
# from webbrowser import open as webopen
# from pywhatkit import search, playonyt
# from dotenv import dotenv_values
# from bs4 import BeautifulSoup
# from rich import print
# from groq import Groq
# import requests
# import os
# import webbrowser
# import subprocess
# import asyncio
# import keyboard
# from typing import List

# env_vars = dotenv_values(".env")

# # groqApi = env_vars.get("groqKey")
# groqApi = os.getenv('groqKey')  

# print("hello ji")
# classes = []

# useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
# client = Groq(api_key=groqApi)

# messages = []

# SystemChatBot = [{'role': 'system', 'message': 'Hello, I am your assistant, how can I help you today?'}]

# IS_WINDOWS = os.name == 'nt'
# IS_LINUX = os.name == 'posix'
# IS_MAC = IS_LINUX and "darwin" in os.sys.platform


# def GoogleSearch(topic):
#     webbrowser.open(f"https://www.google.com/search?q={topic}")
#     return True

# # Function to generate content using AI
# def ContentWriteAi(prompt):
#     messages.append({'role': 'user', 'message': prompt})    
#     completion = client.chat.completions.create(
#         model="mixtral-8x7b-32786",
#         messages=SystemChatBot + messages,
#         max_tokens=2048,
#         temperature=0.7,
#         top_p=1,
#         stream=True,
#         stop=None
#     )
#     Answer = "".join(chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content)
#     messages.append({'role': 'system', 'message': Answer})  
#     return Answer.strip().replace("</s>", "")

# # Function to create content and open in default text editor
# def Content(topic):
#     topic = topic.replace("Content", "").strip()
#     ContentByAi = ContentWriteAi(topic)
#     file_path = os.path.join("data", f"{topic}.txt")
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)
#     with open(file_path, "w", encoding='utf-8') as f:
#         f.write(ContentByAi)
#     subprocess.run(["notepad" if IS_WINDOWS else "nano", file_path])
#     return True

# # Function to search YouTube
# def YouTubeSearch(topic):
#     webbrowser.open(f"https://www.youtube.com/results?search_query={topic}")
#     return True

# # Function to play YouTube videos
# def PlayYouTube(topic):
#     webbrowser.open(f"https://www.youtube.com/results?search_query={topic}")
#     return True

# # Function to open applications (cross-platform)
# def OpenApp(app):
#     try:
#         if IS_WINDOWS:
#             subprocess.Popen(["start", "", app], shell=True)
#         elif IS_LINUX or IS_MAC:
#             subprocess.Popen(["xdg-open" if IS_LINUX else "open", app])
#         return True
#     except Exception as e:
#         print(f"Failed to open app: {e}")
#         return False

# # Function to close applications (Windows only)
# def CloseApp(app):
#     if IS_WINDOWS:
#         try:
#             subprocess.run(["taskkill", "/F", "/IM", f"{app}.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#             return True
#         except Exception as e:
#             print(f"Failed to close {app}: {e}")
#     return False

# # System control commands (volume, mute, etc.)
# def System(command):
#     actions = {
#         'mute': lambda: keyboard.press_and_release("volume mute"),
#         'unmute': lambda: keyboard.press_and_release("volume mute"),
#         'volume up': lambda: keyboard.press_and_release("volume up"),
#         'volume down': lambda: keyboard.press_and_release("volume down")
#     }
#     if command in actions:
#         actions[command]()
#     else:
#         print("Unknown command")
#     return True

# # Function to execute automation commands
# async def translateAndExecute(commands: List[str]):
#     funcs = []
#     for command in commands:
#         cmd = command.lower().strip()
#         if cmd.startswith("open "):
#             funcs.append(asyncio.to_thread(OpenApp, cmd[5:]))
#         elif cmd.startswith("close ") and IS_WINDOWS:
#             funcs.append(asyncio.to_thread(CloseApp, cmd[6:]))
#         elif cmd.startswith("search "):
#             funcs.append(asyncio.to_thread(GoogleSearch, cmd[7:]))
#         elif cmd.startswith("content "):
#             funcs.append(asyncio.to_thread(Content, cmd[8:]))
#         elif cmd.startswith("youtube "):
#             funcs.append(asyncio.to_thread(YouTubeSearch, cmd[8:]))
#         elif cmd.startswith("play "):
#             funcs.append(asyncio.to_thread(PlayYouTube, cmd[5:]))
#         elif cmd.startswith("system "):
#             funcs.append(asyncio.to_thread(System, cmd[7:]))
#         else:
#             print("No valid command found")
#     await asyncio.gather(*funcs)

# # Function to execute automation tasks
# async def AutomationTask(commands: List[str]):
#     await translateAndExecute(commands)
#     return True

# # Example task execution
# async def task():
#     await AutomationTask([
#         "open calculator",
#         "search Python tutorials",
#         "content Python basics",
#         "youtube Python tips",
#         "play Python AI projects",
#         "system volume down"
#     ])

# if __name__ == "__main__":
#     asyncio.run(task())


# def GoogleSearch(topic):
#     webbrowser.open(f"https://www.google.com/search?q={topic}")
#     return True

# def Content(topic):
#     def OpenNotepad(File):
#         default_text_editor = 'notepad.exe'
#         subprocess.Popen([default_text_editor, File])

#     def ContentWriteAi(prompt):
#         messages.append({'role': 'user', 'message': prompt})    

#         completion = client.chat.completions.create(
#             model="mixtral-8x7b-32786",
#             messages=SystemChatBot + messages,
#             max_tokens=2048,
#             temperature=0.7,
#             top_p=1,
#             stream=True,
#             stop=None
#         )

#         Answer = ""

#         for chunk in completion:
#             if chunk.choices[0].delta.content:
#                 Answer += chunk.choices[0].delta.content        

#         Answer = Answer.replace("</s>", "")
#         messages.append({'role': 'system', 'message': Answer})  
#         return Answer
    
#     topic = topic.replace("Content", "")
#     ContentByAi = ContentWriteAi(topic)

#     file_path = rf"data\{topic}.txt"
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)
#     with open(file_path, "w", encoding='utf-8') as f:
#         f.write(ContentByAi)

#     OpenNotepad(file_path)
#     return True 

# def YouTubeSearch(topic):
#     url = f"https://www.youtube.com/results?search_query={topic}"
#     webbrowser.open(url)
#     return True

# def PlayYouTube(topic):
#     playonyt(topic)
#     return True

# def OpenApp(app, sess=requests.Session()):
#     try:
#         aapopen(app, match_closest=True, output=True, throw_error=True)
#         return True
#     except Exception:
#         def extract_links(html):
#             if html is None:
#                 return []
#             soup = BeautifulSoup(html, 'html.parser')
#             links = soup.find_all('a', {'jsname': 'UWckNb'})
#             return [link['href'] for link in links]

#         def search_google(topic):
#             url = f"https://www.google.com/search?q={topic}"
#             headers = {'User-Agent': useragent}
#             response = sess.get(url, headers=headers)
            
#             if response.status_code == 200:
#                 return response.text
#             else:
#                 print("Error:", response.status_code)  
#                 return None
        
#         html = search_google(app)
#         if html:
#             links = extract_links(html)
#             if links:
#                 webopen(links[0])

#         return True
    
# # OpenApp("task manager")
# # PlayYouTube("code with harry")


# def CloseApp(app):
#     if "chrome" in app:
#         return False
#     try:
#         close(app, match_closest=True, output=True, throw_error=True)
#         return True
#     except Exception:
#         return False

# # CloseApp("task manager")

# def System(command):
#     def mute():
#         keyboard.press_and_release("volume mute")
#     def unmute():
#         keyboard.press_and_release("volume mute")
#     def volume_up():
#         keyboard.press_and_release("volume up")
#     def volume_down():
#         keyboard.press_and_release("volume down")
    
#     actions = {
#         'mute': mute,
#         'unmute': unmute,
#         'volume up': volume_up,
#         'volume down': volume_down
#     }

#     if command in actions:
#         actions[command]()
#     else:
#         print("Unknown command")
    
#     return True

# # System('volume down')


# async def translateAndExecute(commands: List[str]):
#     funcs = []

#     for command in commands:
#         if command.startswith("open "):
#             fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
#             funcs.append(fun)
#         elif command.startswith("close "):
#             fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
#             funcs.append(fun)
#         elif command.startswith("search "):
#             fun = asyncio.to_thread(GoogleSearch, command.removeprefix("search "))
#             funcs.append(fun)
#         elif command.startswith("google search "):
#             fun = asyncio.to_thread(GoogleSearch, command.removeprefix("search "))
#             funcs.append(fun)
#         elif command.startswith("content "):
#             fun = asyncio.to_thread(Content, command.removeprefix("content "))
#             funcs.append(fun)
#         elif command.startswith("youtube "):
#             fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube "))
#             funcs.append(fun)
#         elif command.startswith("play "):
#             fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play "))
#             funcs.append(fun)
#         elif command.startswith("system "):
#             fun = asyncio.to_thread(System, command.removeprefix("system "))
#             funcs.append(fun)
#         else:
#             print("No command found")

#     results = await asyncio.gather(*funcs)
    
#     for result in results:
#         if isinstance(result, str):
#             yield result
#         else:
#             yield result

# async def AutomationTask(commands: List[str]):
#     async for result in translateAndExecute(commands):
#         pass
#     return True

# async def task():
#     await AutomationTask(["open task manager", "open file explorar", "search python", "content python", "youtube code with harry", "play python", "system volume down"])
        
# if __name__ == "__main__" :
#     asyncio.run(task())         
     