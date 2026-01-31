import React from 'react';
import ReactMarkdown from 'react-markdown';
import './Message.css';

function Message({ message }) {
  const { role, content, timestamp } = message;
  const isUser = role === 'user';

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={`message ${role}`}>
      <div className={`message-avatar ${role}-avatar`}>
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-body">
        <div className="message-header">
          <span className="message-sender">{isUser ? 'You' : 'TechNova Assistant'}</span>
          <span className="message-time">{formatTime(timestamp)}</span>
        </div>
        <div className="message-content">
          <ReactMarkdown
            components={{
              a: ({ node, ...props }) => (
                <a {...props} target="_blank" rel="noopener noreferrer" />
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

export default Message;
