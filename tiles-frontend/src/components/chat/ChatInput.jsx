import React, { useState, useEffect, useRef } from 'react';
import { ArrowUp } from 'lucide-react';
import PropTypes from 'prop-types';

// Custom CSS for better placeholder visibility on glass background
const customStyles = `
  .chat-input-textarea {
    color: #292524 !important;
  }
  
  .chat-input-textarea::placeholder {
    color: rgba(68, 64, 60, 0.7) !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
  }
  
  .chat-input-textarea:focus::placeholder {
    color: rgba(68, 64, 60, 0.5) !important;
  }
  
  .chat-input-textarea:focus {
    color: #292524 !important;
  }
`;

function ChatInput({ onSendMessage, hasMessages, hasActiveChat = true }) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  // Inject custom styles
  useEffect(() => {
    const styleElement = document.createElement('style');
    styleElement.textContent = customStyles;
    document.head.appendChild(styleElement);
    
    return () => {
      document.head.removeChild(styleElement);
    };
  }, []);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const maxHeight = parseInt(textareaRef.current.style.maxHeight || '100', 10);
      textareaRef.current.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className={`w-full ${hasMessages ? 'pb-2 sm:pb-3' : 'pb-3 sm:pb-5'}`}>
      <div className="max-w-2xl mx-auto px-2 sm:px-0">
        <div className="relative">
          <div className="relative rounded-full shadow-lg" style={{
            background: 'rgba(255, 255, 255, 0.15)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.1)'
          }}>
            <div className="flex items-center p-2.5 gap-2">
              <div className="flex-1 relative">
                <textarea
                  ref={textareaRef}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={hasActiveChat ? "What's on your mind?" : "Click 'Start New Chat' above to begin..."}
                  className="w-full px-3 py-2 bg-transparent border-0 resize-none focus:outline-none text-stone-900 text-base font-normal leading-snug chat-input-textarea"
                  rows="1"
                  style={{
                    minHeight: '40px',
                    maxHeight: '100px',
                    textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
                    color: '#292524'
                  }}
                />
              </div>
              <div className="flex-shrink-0 flex items-center">
                <button
                  onClick={handleSubmit}
                  disabled={!message.trim() || !hasActiveChat}
                  className="h-10 w-10 text-white rounded-full flex items-center justify-center transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none transform hover:scale-105 active:scale-95"
                  style={{
                    background: message.trim() ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' : 'rgba(251, 191, 36, 0.3)',
                    backdropFilter: 'blur(15px)',
                    border: '1px solid rgba(251, 191, 36, 0.4)',
                    boxShadow: message.trim() ? '0 4px 20px rgba(251, 191, 36, 0.3)' : '0 2px 10px rgba(251, 191, 36, 0.1)'
                  }}
                  aria-label="Send message"
                >
                  <ArrowUp className="w-5 h-5" strokeWidth={2.5} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

ChatInput.propTypes = {
  onSendMessage: PropTypes.func.isRequired,
  hasMessages: PropTypes.bool.isRequired,
  hasActiveChat: PropTypes.bool,
};

export default ChatInput;
