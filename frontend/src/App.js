/**
 * @fileoverview Main App component for TechNova Support Portal.
 * Provides the main layout structure with sidebar navigation and chat interface.
 * @author TechNova Solutions
 * @version 1.0.0
 */

import React from 'react';
import ChatBox from './components/ChatBox';
import './App.css';

/**
 * Main application component that renders the support portal interface.
 * 
 * Layout structure:
 * - Sidebar: Contains new chat button, chat history, and branding
 * - Main content: Contains the ChatBox component for user interaction
 * 
 * @component
 * @returns {JSX.Element} The rendered App component with sidebar and main chat area
 * 
 * @example
 * // Usage in index.js
 * <App />
 */
function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-header">
          <button className="new-chat-btn">
            <span>+</span> New Chat
          </button>
        </div>
        <div className="chat-history">
          <div className="chat-history-item active">
            <span className="chat-icon">💬</span>
            <span className="chat-title">Support Chat</span>
          </div>
        </div>
        <div className="sidebar-footer">
          <div className="brand">
            <span className="brand-icon">🚀</span>
            <span className="brand-name">TechNova Support</span>
          </div>
        </div>
      </aside>
      <main className="main-content">
        <ChatBox />
      </main>
    </div>
  );
}

export default App;
