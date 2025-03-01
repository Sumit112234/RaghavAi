from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import dotenv_values
import os
import mtranslate as mt


env_vars = dotenv_values(".env")

inputLanguage = env_vars["inputLanguage"]

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''


HtmlCode = str(HtmlCode).replace("recognition.lang = ''", f"recognition.lang = '{inputLanguage}'") 

with open("data/voice.html", "w") as f:
    f.write(HtmlCode)

current_dir = os.getcwd()

Link = f"{current_dir}/data/voice.html"

chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"   
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--user-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
# chrome_options.add_argument("--headless=new")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)  


TempDirPath = rf"{current_dir}/frontend/files"

def setAssistantStatus(status):
    with open(rf"{TempDirPath}/Status.data", "w" , encoding='utf-8') as f:
        f.write(status)


def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["what", "when", "where", "why", "how", "who", "which", "whom"]
    
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ["?", "." , "!"]:
            new_query = new_query[:-1] + '?'
        else:
            new_query += '?'
    else :
        if query_words[-1][-1] not in ["?", "." , "!"]:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'

    return new_query.capitalize()


def universalTranslator(Text):
    engish_translation = mt.translate(Text, "en", "auto")
    return engish_translation.capitalize()


def speechRecognition():
    driver.get('file:///' + Link)
    driver.find_element(by=By.ID, value="start").click()   

    while True:
        try:
            # print('yes')
            output_element = driver.find_element(by=By.ID, value="output")

            # Wait for text to appear
            WebDriverWait(driver, 10).until(lambda d: output_element.text.strip() != "")
            
            Text = output_element.text
            if Text:
                driver.find_element(by=By.ID, value="end").click()

                if inputLanguage == "en":
                    return QueryModifier(Text)
                else:
                    setAssistantStatus("Translating your query to English")
                    return QueryModifier(universalTranslator(Text)) 
            else:
                print('no text found')
                
        except Exception as e:
            print(e)
            pass
 

 
      

    

if __name__ == "__main__":
     while True:
         Text = speechRecognition()
         print(Text)