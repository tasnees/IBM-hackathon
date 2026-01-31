import React from 'react';
import ChatBox from './components/ChatBox';
import './App.css';

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
