from googlesearch import search
from groq import Groq
from json import load,dump
import datetime
from dotenv import dotenv_values
import os



env_vars = dotenv_values(".env")

userName = env_vars["userName"]
assistantname = env_vars["assistantName"]
GroqApiKey = env_vars["groqKey"]

client = Groq(api_key=GroqApiKey)

messages = []

System = f"""Hello, I am {userName}, You are a very accurate and advanced AI chatbot named {assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

systemChatBot = [
    {"role" : "system", "content" : f"{System}"}
    
]

try:
    if os.stat(r"data\ChatLog.json").st_size == 0:  # Check if file is empty
        messages = []
    else:
        with open(r"data\ChatLog.json", "r") as f:
            messages = load(f)
except (FileNotFoundError):  # Handle both file missing and empty JSON
    messages = []
    with open(r"data\ChatLog.json", "w") as f:
        dump([], f, indent=4)


def GoogleSearch(query):
    results = list(search(query, advanced=True , num_results=5))
    Answer = f"The search results for your query are : \n[start]"

    for i in results:
        Answer += f"Title : {i.title}\nDescription : {i.description}\n\n"

    Answer += "[end]"
    return Answer
    




def RealtimeInfomation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")        
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H") 
    minute = current_date_time.strftime("%M")   
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed, \n"
    data += f"Day : {day}\nDate : {date}\nMonth : {month}\nYear : {year}\nTime : {hour}:{minute}:{second}\n"
    
    return data

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip() != ""]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def realTimeChatBot(prompt):
    global systemChatBot , messages

    try :
        with open(r"data\ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role" : "user", "content" : f"{prompt}"})  
        systemChatBot.append({"role" : "user", "content" : GoogleSearch(prompt) })  

        

        completion = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=systemChatBot + [{"role" : "system", "content" : RealtimeInfomation()}] + messages,   
            max_tokens=1024,
            temperature=0.7,
            top_p=1.0,
            stream=True,
            stop=None 
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        
        messages.append({"role" : "assistant", "content" : Answer})

        with open(r"data\ChatLog.json", "w") as f:
            dump(messages,f, indent=4)

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error : {e}")   
        with open(r"data\ChatLog.json", "w") as f:
            dump([],f, indent=4)
        return realTimeChatBot(Query)
    

if __name__ == "__main__" :
    while True:
        Query = input("Enter the Question : ")
        print(realTimeChatBot(Query))