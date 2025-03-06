from googlesearch import search
from groq import Groq
import datetime
from dotenv import dotenv_values
import os


# Load environment variables
env_vars = dotenv_values(".env")

# userName = env_vars["userName"]
# assistantname = env_vars["assistantName"]
# GroqApiKey = env_vars["groqKey"]
userName = os.getenv('userName')
assistantname = os.getenv('assistantName')
GroqApiKey = os.getenv('groqKey')

client = Groq(api_key=GroqApiKey)

# Message history in memory
messages = []

System = f"""Hello, I am {userName}, You are a very accurate and advanced AI chatbot named {assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

systemChatBot = [{"role": "system", "content": System}]

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = "The search results for your query are:\n[start]\n"
    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return (f"Please use this real-time information if needed,\n"
            f"Day: {current_date_time.strftime('%A')}\n"
            f"Date: {current_date_time.strftime('%d')}\n"
            f"Month: {current_date_time.strftime('%B')}\n"
            f"Year: {current_date_time.strftime('%Y')}\n"
            f"Time: {current_date_time.strftime('%H:%M:%S')}\n")

def AnswerModifier(Answer):
    return '\n'.join([line for line in Answer.split('\n') if line.strip()])

def realTimeChatBot(prompt):
    global messages, systemChatBot
    try:
        messages.append({"role": "user", "content": prompt})
        systemChatBot.append({"role": "user", "content": GoogleSearch(prompt)})
        
        completion = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=systemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
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
        messages.append({"role": "assistant", "content": Answer})
        return AnswerModifier(Answer)
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request."

if __name__ == "__main__":
    while True:
        Query = input("Enter the Question: ")
        print(realTimeChatBot(Query))
