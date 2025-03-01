from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import asyncio
# from Automation import AutomationTask 
from Chatbot import ChatBot
from model import FirstLayerDMM
from realTimeSearchEngine import realTimeChatBot


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route('/', methods=['GET'])
def main():
    return jsonify({"response": "Server Started."})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_query = data.get("query", "")
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    response = ChatBot(user_query)
    return jsonify({"response": response})

@app.route('/get-query-details', methods=['POST'])
def getQueryDetails():
    data = request.get_json()
    user_query = data.get("query", "")
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    response = FirstLayerDMM(user_query)
    return jsonify({"response": response})

@app.route('/chat-realtime', methods=['POST'])
def getrealTimeChat():
    data = request.get_json()
    user_query = data.get("query", "")
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400
    
    response = realTimeChatBot(user_query)
    return jsonify({"response": response})


# @app.route('/automation-task', methods=['POST'])
# @cross_origin()
# def automation_task():
#     try:
#         data = request.get_json()
#         commands = data.get("commands", [])

#         if not commands:
#             return jsonify({"error": "No commands provided"}), 400

#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         result = loop.run_until_complete(AutomationTask(commands))

#         # Generate user-friendly messages
#         task_messages = []
#         for command in commands:
#             if command.startswith("open"):
#                 task_messages.append(f"Opening {command.replace('open ', '')}")
#             elif command.startswith("close"):
#                 task_messages.append(f"Closing {command.replace('close ', '')}")
#             elif command.startswith("play"):
#                 task_messages.append(f"Playing {command.replace('play ', '')}")
#             elif command.startswith("google search"):
#                 task_messages.append(f"Searching Google for {command.replace('google search ', '')}")
#             elif command.startswith("youtube search"):
#                 task_messages.append(f"Searching YouTube for {command.replace('youtube search ', '')}")
#             else:
#                 task_messages.append(f"Executing {command}...")

#         return jsonify({
#             "message": "Automation executed successfully!",
#             "result": task_messages  # Send a list of descriptive messages
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route('/automation-task', methods=['POST'])
# @cross_origin()
# def automationTask():
#     data = request.get_json()
#     user_query = data.get("query", "")
    
#     if not user_query:
#         return jsonify({"error": "No query provided"}), 400
    
#     response = Automation(user_query)
#     return jsonify({"response": response})

# @app.route('/get-voice', methods=['POST'])
# def getvoice():
#     data = request.get_json()
#     user_query = data.get("query", "")
    
#     if not user_query:
#         return jsonify({"error": "No query provided"}), 400
    
#     TextToSpeech(user_query)
#     return jsonify({"response": "success"})

# @app.route('/speech-to-text', methods=['GET'])
# def speech_to_text():
#     try:
#         text = speechRecognition()  # Capture speech input
#         return jsonify({"transcript": text})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
