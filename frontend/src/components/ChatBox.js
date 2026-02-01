/**
 * @fileoverview ChatBox component - ChatGPT-style interface for TechNova Support.
 * Pure React chatbox that connects to IBM watsonx Orchestrate agent via API.
 * @author TechNova Solutions
 * @version 3.0.0
 */

import React, { useState, useRef, useEffect } from "react";
import "./ChatBox.css";
import Message from "./Message";
import watsonxAgent from "../services/watsonxAgent";

/**
 * ChatGPT-style chatbox that connects to IBM watsonx Orchestrate agent.
 */
function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Initialize connection
  useEffect(() => {
    // Add welcome message
    setMessages([
      {
        id: 1,
        role: "assistant",
        content: "Hello! I'm the TechNova Support Assistant powered by IBM watsonx Orchestrate. How can I help you today?\n\nI can help you with:\n• Creating ServiceNow incidents\n• Reporting bugs (GitHub issues)\n• Getting support for TechNova products",
        timestamp: new Date(),
      },
    ]);
    setIsConnected(watsonxAgent.isConfigured());
  }, []);

  /**
   * Send message to the IBM watsonx Orchestrate agent
   */
  const sendMessageToAgent = async (userMessage) => {
    try {
      const response = await watsonxAgent.sendMessage(userMessage);
      return response;
    } catch (error) {
      console.error("[ChatBox] Error sending message:", error);
      
      if (!watsonxAgent.isConfigured()) {
        return "⚠️ **API Key Required**\n\nTo connect to the IBM watsonx Orchestrate agent, please set your API key in the `.env` file:\n\n```\nREACT_APP_WXO_API_KEY=your_api_key_here\n```\n\nThen restart the development server.";
      }
      
      return `I'm having trouble connecting to the agent.\n\n**Error:** ${error.message}\n\nPlease check:\n• API key is valid\n• Agent is deployed and running`;
    }
  };

  /**
   * Handle sending a message
   */
  const handleSend = async () => {
    const trimmedInput = inputValue.trim();
    if (!trimmedInput || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      role: "user",
      content: trimmedInput,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // Get response from agent
    const agentResponse = await sendMessageToAgent(trimmedInput);

    // Add assistant message
    const assistantMessage = {
      id: Date.now() + 1,
      role: "assistant",
      content: agentResponse,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setIsLoading(false);
  };

  /**
   * Handle Enter key press
   */
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chatbox">
      <div className="chatbox-header">
        <h1>TechNova Support</h1>
        <span className={`model-badge ${isConnected ? "connected" : ""}`}>
          <img
            src="https://www.ibm.com/favicon.ico"
            alt="IBM"
            style={{ width: "16px", height: "16px", marginRight: "6px", verticalAlign: "middle" }}
          />
          watsonx Orchestrate
          {isConnected ? " Connected" : " Connecting..."}
        </span>
      </div>

      <div className="messages-container">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <div className="input-wrapper">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe your issue or ask a question..."
            rows={1}
            disabled={isLoading}
          />
          <button
            className="send-button"
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
          >
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
        <p className="disclaimer">Powered by IBM watsonx Orchestrate</p>
      </div>
    </div>
  );
}

export default ChatBox;
