import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import type { ChatMessage, ChatResponse } from '@/types';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isLoading
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const message = input.trim();
    setInput('');
    await onSendMessage(message);
  };

  const formatMessage = (content: string) => {
    const parts = content.split(/(\[[\w_]+\])/g);
    return parts.map((part, idx) => {
      if (part.match(/\[[\w_]+\]/)) {
        return <span key={idx} className="citation">{part}</span>;
      }
      return <span key={idx}>{part}</span>;
    });
  };

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <h3>Welcome to your Family Office AI Advisor</h3>
            <p>Ask me about:</p>
            <ul>
              <li>Tax optimization strategies</li>
              <li>Investment allocation recommendations</li>
              <li>Estate and trust planning</li>
              <li>Comprehensive wealth management</li>
            </ul>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message message-${msg.role}`}>
            <div className="message-role">
              {msg.role === 'user' ? 'You' : 'Family Office Advisor'}
            </div>
            <div className="message-content">
              {formatMessage(msg.content)}
            </div>
            {msg.timestamp && (
              <div className="message-timestamp">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="message message-assistant">
            <div className="message-role">Family Office Advisor</div>
            <div className="message-content loading">
              <Loader2 className="spinner" />
              <span>Analyzing your situation...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about tax strategies, investments, or estate planning..."
          disabled={isLoading}
          className="chat-input"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="btn btn-primary btn-icon"
        >
          {isLoading ? <Loader2 className="spinner" /> : <Send size={20} />}
        </button>
      </form>
    </div>
  );
};
