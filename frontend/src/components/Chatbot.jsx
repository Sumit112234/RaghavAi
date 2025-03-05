import { useState, useRef, useEffect } from "react";
import { Mic, Send, MessageSquare, Circle, Loader } from "lucide-react";

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [assistantState, setAssistantState] = useState("idle"); // idle, listening, thinking, responding
  const [speechInput, setSpeechInput] = useState(""); // State to track speech input
  const queryTypeRef = useRef([]);

  const chatBoxRef = useRef(null);
  const recognitionRef = useRef(null);

  // Effect for animated gradient background
  useEffect(() => {
    const interval = setInterval(() => {
      document.querySelector(".gradient-bg").style.backgroundPosition = `${Math.random() * 100}% ${Math.random() * 100}%`;
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const getQueryDetails = async (inputText) => {
    setAssistantState("thinking");
    try {
      const response = await fetch("https://raghav-aiserver.vercel.app/get-query-details", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: inputText }),
      });
      const data = await response.json();
      console.log('data', data.response);
      queryTypeRef.current = data?.response || [];
      return data?.response;
    } catch (error) {
      console.error("Unable to connect to backend.");
      return [];
    }
  };

  const speak = (text) => {
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    speech.rate = 1;
    speech.pitch = 1;
    speech.onstart = () => setAssistantState("responding");
    speech.onend = () => setAssistantState("idle");
    window.speechSynthesis.speak(speech);
  };

  const AskToChatbot = async (inputText) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: inputText }),
      });

      const data = await response.json();
      setMessages((prev) => [...prev, { sender: "Raghav", text: data.response }]);
      speak(data.response);

      setTimeout(() => {
        chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
      }, 100);
    } catch (error) {
      setMessages((prev) => [...prev, { sender: "Error", text: "Unable to connect to backend." }]);
      setAssistantState("idle");
    }
  };

  const AskToGoogle = async (inputText) => {
    try {
      const response = await fetch("https://raghav-aiserver.vercel.app/chat-realtime", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: inputText }),
      });

      const data = await response.json();
      setMessages((prev) => [...prev, { sender: "Raghav", text: data.response }]);
      speak(data.response);

      setTimeout(() => {
        chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
      }, 100);
    } catch (error) {
      setMessages((prev) => [...prev, { sender: "Error", text: "Unable to connect to backend." }]);
      setAssistantState("idle");
    }
  };

  const AutomationTask = async (commands) => {
    try {
      console.log("Sending commands:", commands);
      const response = await fetch("https://raghav-aiserver.vercel.app/automation-task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ commands }),
      });

      const data = await response.json();

      if (!data.result || data.result.length === 0) {
        setMessages((prev) => [...prev, { sender: "Raghav", text: "No valid automation tasks found." }]);
        setAssistantState("idle");
        return;
      }

      let botResponse = "";
      data.result.forEach((taskMessage) => {
        botResponse += taskMessage + ', ';
      });
      botResponse += ` Automation tasks executed successfully Sir.`;

      setMessages((prev) => [...prev, { sender: "Raghav", text: botResponse }]);
      speak(botResponse);

      setTimeout(() => {
        chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
      }, 100);
    } catch (error) {
      setMessages((prev) => [...prev, { sender: "Error", text: "Unable to connect to backend." }]);
      setAssistantState("idle");
    }
  };

  const checkAndSet = async (inputText) => {
    const queryType = queryTypeRef.current;
    if (!queryType || queryType.length === 0) {
      console.log("No query found!");
      setAssistantState("idle");
      return;
    }

    let automationCommands = [];

    for (const query of queryType) {
      let words = query.split(" ");
      let action = words[0];
      let task = words.slice(1).join(" ");

      if (["google search", "youtube search"].includes(words.slice(0, 2).join(" "))) {
        action = words.slice(0, 2).join(" ");
        task = words.slice(2).join(" ");
      }

      if (action === "general") {
        await AskToChatbot(inputText);
      } else if (action === "realtime") {
        await AskToGoogle(inputText);
      } else if (["open", "close", "system", "content", "google search", "youtube search", "reminder", "play"].includes(action)) {
        automationCommands.push(query);
      } else {
        console.log("Unknown query:", query);
      }
    }

    if (automationCommands.length > 0) {
      await AutomationTask(automationCommands);
    } else {
      setAssistantState("idle");
    }
  };

  const sendMessage = async (event) => {
    if (event) event.preventDefault();
    
    // Determine which input to use (text or speech)
    const inputToSend = userInput.trim() || speechInput.trim();
    if (!inputToSend) return;

    // Add the message to the chat
    setMessages((prev) => [...prev, { sender: "You", text: inputToSend }]);
    
    // Clear both inputs
    setUserInput("");
    setSpeechInput("");
    
    // Scroll to bottom
    setTimeout(() => {
      if (chatBoxRef.current) {
        chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
      }
    }, 100);

    // Process the message
    const queryTypes = await getQueryDetails(inputToSend);
    queryTypeRef.current = queryTypes;
    await checkAndSet(inputToSend);
  };

  const handleVoiceInput = () => {
    // If already listening, stop
    if (assistantState === "listening") {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setAssistantState("idle");
      return;
    }

    // Check browser support
    if (!window.SpeechRecognition && !window.webkitSpeechRecognition) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }

    setAssistantState("listening");
    setSpeechInput(""); // Clear previous speech input
    
    // Initialize speech recognition
    recognitionRef.current = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognitionRef.current.lang = "en-US";
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = true;

    recognitionRef.current.onstart = () => {
      console.log("Listening...");
      setAssistantState("listening");
    };
    
    recognitionRef.current.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setAssistantState("idle");
    };
    
    recognitionRef.current.onend = () => {
      setAssistantState("idle");
      
      // Automatically send the message when speech recognition ends
      // Only if we have collected some speech input
      if (speechInput.trim()) {
        setTimeout(() => {
          sendMessage();
        }, 500); // Small delay to ensure UI updates first
      }
    };
    
    recognitionRef.current.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setUserInput(transcript); // Update the text input with speech
      setSpeechInput(transcript); // Store in speech input state
      
      if (event.results[0].isFinal) {
        // Once we have the final result, stop listening
        // The onend handler will trigger sendMessage
        recognitionRef.current.stop();
      }
    };

    recognitionRef.current.start();
  };

  // Determine the assistant animation based on state
  const getAssistantAnimation = () => {
    switch (assistantState) {
      case "listening":
        return "assistant-listening";
      case "thinking":
        return "assistant-thinking";
      case "responding":
        return "assistant-responding";
      default:
        return "";
    }
  };

  // Get assistant status text
  const getAssistantStatus = () => {
    switch (assistantState) {
      case "listening":
        return "Listening...";
      case "thinking":
        return "Thinking...";
      case "responding":
        return "Responding...";
      default:
        return "How can I help you?";
    }
  };

  return (
    <div className="flex flex-col items-center justify-center  min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-blue-900 text-white relative overflow-hidden">
      {/* Animated background */}
      <div className="gradient-bg absolute inset-0 bg-gradient-to-br from-indigo-600/20 via-purple-600/20 to-blue-600/20 bg-[length:400%_400%] transition-all duration-3000 ease-in-out"></div>
      
      {/* Glowing orbs */}
      <div className="absolute top-1/4 left-1/4 w-32 h-32 rounded-full bg-blue-500/10 blur-xl"></div>
      <div className="absolute bottom-1/4 right-1/3 w-40 h-40 rounded-full bg-purple-500/10 blur-xl"></div>
      
      <div className="relative z-10 w-full max-w-md px-4">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400 mb-1">
            Raghav AI
          </h1>
          <p className="text-blue-200 text-sm">{getAssistantStatus()}</p>
        </div>
        
        {/* AI Avatar */}
        <div className="flex justify-center mb-6">
          <div className={`relative w-20 h-20 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center ${getAssistantAnimation()}`}>
            <div className="absolute inset-1 rounded-full bg-gray-900 flex items-center justify-center overflow-hidden">
              <div className={`w-full h-full flex items-center justify-center ${assistantState !== 'idle' ? 'animate-pulse' : ''}`}>
                {assistantState === "listening" && (
                  <div className="flex space-x-1">
                    {[1, 2, 3, 4].map((i) => (
                      <div 
                        key={i} 
                        className="w-1 bg-blue-400 rounded-full animate-soundwave" 
                        style={{ 
                          height: `${Math.random() * 16 + 4}px`,
                          animationDelay: `${i * 0.1}s`
                        }}
                      />
                    ))}
                  </div>
                )}
                
                {assistantState === "thinking" && (
                  <Loader size={24} className="text-blue-400 animate-spin" />
                )}
                
                {assistantState === "responding" && (
                  <div className="flex space-x-1">
                    {[1, 2, 3].map((i) => (
                      <div 
                        key={i} 
                        className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" 
                        style={{ animationDelay: `${i * 0.15}s` }}
                      />
                    ))}
                  </div>
                )}
                
                {assistantState === "idle" && (
                  <MessageSquare size={24} className="text-blue-400" />
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* Chat Container */}
        <div ref={chatBoxRef} className="bg-gray-900/80 backdrop-blur-lg rounded-lg p-4 h-96 overflow-y-auto mb-4 border border-gray-700/50 shadow-xl">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 text-center">
              <MessageSquare size={40} className="mb-2 text-gray-600" />
              <p>Hello! I'm Raghav, your AI assistant.</p>
              <p className="text-sm mt-1">Ask me anything or give me a command.</p>
            </div>
          )}
          
          {messages.map((msg, index) => (
            <div 
              key={index} 
              className={`mb-3 flex ${msg.sender === "You" ? "justify-end" : "justify-start"}`}
            >
              <div 
                className={`px-4 py-2 rounded-2xl max-w-xs lg:max-w-md break-words ${
                  msg.sender === "You" 
                    ? "bg-gradient-to-r from-blue-600 to-blue-700 rounded-tr-none"
                    : "bg-gradient-to-r from-purple-700 to-indigo-800 rounded-tl-none"
                }`}
              >
                {msg.text}
                <div className="text-xs text-blue-200/60 mt-1 text-right">
                  {msg.sender === "You" ? "You" : "Raghav"}
                </div>
              </div>
            </div>
          ))}
          
          {assistantState === "thinking" && (
            <div className="flex justify-start mb-3">
              <div className="px-4 py-3 rounded-2xl bg-gradient-to-r from-purple-700/50 to-indigo-800/50 rounded-tl-none flex items-center">
                <div className="flex space-x-1">
                  {[0, 1, 2].map((i) => (
                    <div 
                      key={i} 
                      className="w-2 h-2 bg-blue-400/70 rounded-full animate-bounce" 
                      style={{ animationDelay: `${i * 0.15}s` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Input Form */}
        <form 
          onSubmit={sendMessage} 
          className="relative flex items-center w-full"
        >
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Message Raghav..."
            className="w-full p-4 pr-24 rounded-full bg-gray-800/80 backdrop-blur-sm border border-gray-700/50 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            disabled={assistantState === "thinking" || assistantState === "responding"}
          />
          
          <div className="absolute right-2 flex space-x-1">
            <button 
              type="button" 
              onClick={handleVoiceInput} 
              className={`p-3 rounded-full transition-all duration-200 ${
                assistantState === "listening" 
                  ? "bg-red-500 hover:bg-red-600" 
                  : "bg-blue-600 hover:bg-blue-700"
              }`}
              disabled={assistantState === "thinking" || assistantState === "responding"}
            >
              <Mic size={18} className={assistantState === "listening" ? "animate-pulse" : ""} />
            </button>
            
            <button 
              type="submit" 
              className="p-3 rounded-full bg-purple-600 hover:bg-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!userInput.trim() || assistantState === "thinking" || assistantState === "responding"}
            >
              <Send size={18} />
            </button>
          </div>
        </form>
      </div>
      
      {/* CSS for animations */}
      <style jsx>{`
        @keyframes soundwave {
          0%, 100% { height: 4px; }
          50% { height: 16px; }
        }
        
        .animate-soundwave {
          animation: soundwave 0.9s ease-in-out infinite;
        }
        
        .assistant-listening {
          box-shadow: 0 0 0 rgba(59, 130, 246, 0.5);
          animation: pulse-blue 2s infinite;
        }
        
        .assistant-thinking {
          box-shadow: 0 0 0 rgba(139, 92, 246, 0.5);
          animation: pulse-purple 2s infinite;
        }
        
        .assistant-responding {
          box-shadow: 0 0 0 rgba(16, 185, 129, 0.5);
          animation: pulse-multi 2s infinite;
        }
        
        @keyframes pulse-blue {
          0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
          70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); }
          100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
        }
        
        @keyframes pulse-purple {
          0% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.7); }
          70% { box-shadow: 0 0 0 10px rgba(139, 92, 246, 0); }
          100% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0); }
        }
        
        @keyframes pulse-multi {
          0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
          70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
          100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
      `}</style>
    </div>
  );
};

export default Chatbot;