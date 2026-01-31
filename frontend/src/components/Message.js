/**
 * @fileoverview Message component for displaying chat messages.
 * Renders individual messages in the chat interface with different
 * styling for user and assistant messages, supporting Markdown content.
 * @author TechNova Solutions
 * @version 1.0.0
 */

import React from 'react';
import ReactMarkdown from 'react-markdown';
import './Message.css';

/**
 * A single message bubble component in the chat interface.
 * Displays messages with different styling based on sender role.
 * Supports Markdown rendering for assistant responses.
 * 
 * @component
 * @param {Object} props - Component props
 * @param {Object} props.message - The message object containing message data
 * @param {string} props.message.role - The sender role ('user' or 'assistant')
 * @param {string} props.message.content - The message text content (supports Markdown)
 * @param {Date} props.message.timestamp - When the message was sent
 * @returns {JSX.Element} A styled message bubble with avatar, sender name, timestamp, and content
 * 
 * @example
 * // User message
 * <Message message={{ role: 'user', content: 'I need help', timestamp: new Date() }} />
 * 
 * @example
 * // Assistant response with Markdown
 * <Message message={{ 
 *   role: 'assistant', 
 *   content: '**Incident created!** Reference: INC0010001',
 *   timestamp: new Date() 
 * }} />
 */
function Message({ message }) {
  const { role, content, timestamp } = message;
  const isUser = role === 'user';

  /**
   * Formats a Date object into a localized time string.
   * @param {Date} date - The date to format
   * @returns {string} Formatted time string (e.g., "10:30 AM")
   */
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
