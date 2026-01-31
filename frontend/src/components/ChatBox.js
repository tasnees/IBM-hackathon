import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import './ChatBox.css';

// Use relative path so nginx can proxy to the backend
// In development, set REACT_APP_API_URL=http://localhost:8000
const API_URL = process.env.REACT_APP_API_URL || '/api';

// IBM watsonx Orchestrate Configuration
const WXO_CONFIG = {
  orchestrationID: "20260130-2119-1725-5086-83dec47ef685_20260130-2119-4901-9095-cc228da9e153",
  hostURL: "https://dl.watson-orchestrate.ibm.com",
  rootElementID: "wxo-chat-root",
  chatOptions: {
    agentId: "8c0ba06c-3f61-44ec-a792-da95a88b27a6",
  }
};

const WELCOME_MESSAGE = {
  id: 'welcome',
  role: 'assistant',
  content: `👋 Hello! I'm the TechNova Support Assistant.

I can help you with:
- **Creating IT incidents** in ServiceNow
- **Reporting bugs** and technical issues
- **Access requests** and permissions
- **General IT support** questions

Just describe your issue and I'll help you create a support ticket!`,
  timestamp: new Date(),
};

function ChatBox() {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load IBM watsonx Orchestrate Chat Widget
  useEffect(() => {
    window.wxOConfiguration = WXO_CONFIG;

    const loadWxOScript = () => {
      const script = document.createElement('script');
      script.src = `${WXO_CONFIG.hostURL}/wxochat/wxoLoader.js?embed=true`;
      script.addEventListener('load', () => {
        if (window.wxoLoader) {
          window.wxoLoader.init();
        }
      });
      document.head.appendChild(script);
    };

    // Load the script after a short delay to ensure DOM is ready
    const timer = setTimeout(loadWxOScript, 0);

    return () => {
      clearTimeout(timer);
    };
  }, []);

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    // Auto-resize textarea
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      // Call the support API
      const response = await fetch(`${API_URL}/get_support`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          short_description: userMessage.content.substring(0, 100),
          description: userMessage.content,
          urgency_value: '3',
          impact_value: '3',
          assignment_group: 'IT-Support',
          incident_category: 'Error / Bug',
          caller_username: 'chat_user',
        }),
      });

      const data = await response.json();

      let assistantContent;
      if (data.success) {
        assistantContent = `✅ **Incident Created Successfully!**

**Incident Number:** ${data.incident_number}

**Details:**
- Your issue has been logged in ServiceNow
- ${data.slack_message_sent ? '📢 The support team has been notified via Slack' : ''}
- ${data.github_issue_created ? `🐛 A GitHub issue has been created: [View Issue](${data.github_issue_url})` : ''}

A support engineer will review your ticket shortly. Is there anything else I can help you with?`;
      } else {
        assistantContent = `❌ **Unable to create incident**

${data.error_details?.error_message || 'An unexpected error occurred.'}

Please try again or contact support directly.`;
      }

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `⚠️ **Connection Error**

Unable to reach the support server. Please check your connection and try again.

Error: ${error.message}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbox">
      <div className="chatbox-header">
        <h1>TechNova Support</h1>
        <span className="model-badge">AI Assistant</span>
      </div>

      <div className="messages-container">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar assistant-avatar">🤖</div>
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
            ref={textareaRef}
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Describe your issue..."
            rows={1}
            disabled={isLoading}
          />
          <button
            className="send-button"
            onClick={handleSubmit}
            disabled={!inputValue.trim() || isLoading}
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M22 2L11 13"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M22 2L15 22L11 13L2 9L22 2Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
        <p className="disclaimer">
          TechNova Support creates real tickets in ServiceNow. Please provide accurate information.
        </p>
      </div>

      {/* IBM watsonx Orchestrate Chat Widget Container */}
      <div id="wxo-chat-root"></div>
    </div>
  );
}

export default ChatBox;
