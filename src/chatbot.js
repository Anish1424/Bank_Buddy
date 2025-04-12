import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Chatbot.css";

const Chatbot = () => {
  const [query, setQuery] = useState("");
  const [chat, setChat] = useState([]);
  const [userId] = useState("user_123");
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(true);

  const speak = (text) => {
    if (!isSpeaking) return;
    window.speechSynthesis.cancel(); // Stop any ongoing speech before starting a new one
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 1;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  };

  const toggleSpeech = () => {
    setIsSpeaking((prev) => {
      if (!prev) {
        window.speechSynthesis.cancel();
      }
      return !prev;
    });
  };

  const sendMessage = async () => {
    if (!query.trim()) return;

    const newChat = [...chat, { sender: "user", message: query }];
    setChat(newChat);
    setQuery("");
    setIsLoading(true);

    try {
      const response = await axios.post("http://localhost:5000/chat", {
        query,
        user_id: userId,
      });
      
      const botMessage = response.data.response;
      setChat([...newChat, { sender: "bot", message: botMessage }]);
      speak(botMessage);
    } catch (error) {
      const errorMessage = "⚠️ Server error. Try again.";
      setChat([...newChat, { sender: "bot", message: errorMessage }]);
      speak(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = false;
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onresult = (event) => {
      const speechText = event.results[0][0].transcript;
      setQuery(speechText);
    };

    if (isListening) recognition.start();

    return () => recognition.stop();
  }, [isListening]);

  return (
    <div className={`chat-container ${isListening ? "ai-glow" : ""}`}>
      <h2 className="chat-title">🤖 Banking Chatbot</h2>

      <div className="chat-box">
        {chat.map((msg, index) => (
          <div key={index} className={`chat-bubble ${msg.sender}`}>
            {msg.message}
          </div>
        ))}
        {isLoading && <div className="chat-bubble bot typing-dots">...</div>}
      </div>

      <div className="input-container">
        <input
          type="text"
          className="input-box"
          placeholder="Ask me anything..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="send-button" onClick={sendMessage}>Send</button>
        <button className={`mic-button ${isListening ? "active" : ""}`} onClick={() => setIsListening(true)}>🎤</button>
        <button className="toggle-speech-button" onClick={toggleSpeech}>{isSpeaking ? "🔊 Mute" : "🔈 Unmute"}</button>
      </div>
    </div>
  );
};

export default Chatbot;
