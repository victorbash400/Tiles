import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { useState } from 'react';

export default function ChatBubble({ message, isUser, timestamp, aiSuggestions, isGenerating, chatId }) {
  // Define base classes for bubbles and text
  const bubbleBaseClasses = "px-4 py-3 rounded-2xl shadow-sm";
  const textBaseClasses = "text-sm whitespace-pre-wrap break-words m-0 leading-relaxed";

  // Define classes for user bubbles - warm amber theme
  const userBubbleClasses = `bg-gradient-to-r from-amber-500 to-amber-600 text-white ${bubbleBaseClasses}`;
  const userTimestampClasses = "text-xs text-stone-500";

  // Define classes for AI bubbles - clean white background
  const aiBubbleClasses = `bg-white/80 backdrop-blur-sm border border-stone-200/50 ${bubbleBaseClasses}`;
  const aiTextClasses = `text-stone-800 ${textBaseClasses}`;
  const aiTimestampClasses = "text-xs text-stone-500";

  // AI Typing Animation Component (handles both thinking and generating)
  const TypingAnimation = () => {
    // Determine if this is likely content generation based on context
    const isGenerating = aiSuggestions?.ready_to_generate || aiSuggestions?.has_content;
    
    return (
      <div className="flex items-center space-x-4 py-4">
        {/* Sophisticated animated loader */}
        <div className="relative">
          {isGenerating ? (
            // More complex animation for generation
            <>
              <motion.div 
                className="w-8 h-8 rounded-full border-2 border-amber-200"
                animate={{ rotate: 360 }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  ease: "linear"
                }}
              />
              <motion.div 
                className="absolute inset-0 w-8 h-8 rounded-full border-2 border-transparent border-t-amber-500 border-r-amber-400"
                animate={{ rotate: 360 }}
                transition={{ 
                  duration: 1.5, 
                  repeat: Infinity,
                  ease: "linear"
                }}
              />
              <motion.div 
                className="absolute inset-1 w-6 h-6 rounded-full bg-gradient-to-r from-amber-100 to-amber-200"
                animate={{ 
                  scale: [0.8, 1, 0.8],
                  opacity: [0.5, 1, 0.5]
                }}
                transition={{ 
                  duration: 1, 
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            </>
          ) : (
            // Simpler breathing animation for thinking
            <>
              <motion.div 
                className="w-6 h-6 rounded-full bg-gradient-to-r from-amber-100 to-amber-200 opacity-30"
                animate={{ 
                  scale: [1, 1.1, 1],
                  opacity: [0.3, 0.6, 0.3]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
              <motion.div 
                className="absolute inset-0 w-6 h-6 rounded-full bg-gradient-to-r from-amber-200 to-amber-300 opacity-20"
                animate={{ 
                  scale: [1.1, 1.3, 1.1],
                  opacity: [0.2, 0.4, 0.2]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 0.5
                }}
              />
            </>
          )}
        </div>
        
        {/* Animated dots */}
        <div className="flex items-center space-x-1.5">
          <motion.div 
            className="w-2 h-2 rounded-full bg-gradient-to-r from-amber-400 to-amber-500"
            animate={{ 
              scale: [1, 1.3, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{ 
              duration: 1.2, 
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <motion.div 
            className="w-2 h-2 rounded-full bg-gradient-to-r from-amber-400 to-amber-500"
            animate={{ 
              scale: [1, 1.3, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{ 
              duration: 1.2, 
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0.2
            }}
          />
          <motion.div 
            className="w-2 h-2 rounded-full bg-gradient-to-r from-amber-400 to-amber-500"
            animate={{ 
              scale: [1, 1.3, 1],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{ 
              duration: 1.2, 
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0.4
            }}
          />
        </div>
        
        {/* Context-aware message */}
        <div className="text-sm">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <motion.span 
              className="font-semibold bg-gradient-to-r from-amber-700 via-amber-600 to-amber-500 bg-clip-text text-transparent"
              animate={{ opacity: [0.7, 1, 0.7] }}
              transition={{ 
                duration: 1.5, 
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              {isGenerating ? 'Curating your perfect event' : 'Tiles is thinking'}
            </motion.span>
            <br />
            <motion.span 
              className="text-xs text-stone-600 font-medium"
              animate={{ opacity: [0.6, 1, 0.6] }}
              transition={{ 
                duration: 1.2, 
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              {isGenerating 
                ? 'Generating personalized recommendations...' 
                : 'Preparing your response...'
              }
            </motion.span>
          </motion.div>
        </div>
      </div>
    );
  };


  // PDF Download Section Component with loading states
  const PDFDownloadSection = ({ chatId }) => {
    const [isDownloading, setIsDownloading] = useState(false);

    const handleDownload = async () => {
      if (isDownloading) return; // Prevent multiple clicks
      
      setIsDownloading(true);
      try {
        const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';
        const sessionId = chatId || 'default';
        
        const response = await fetch(`${API_BASE_URL}/generate-pdf/${sessionId}`, {
          method: 'POST'
        });
        
        if (response.ok) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `event_plan_${sessionId}.pdf`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        } else {
          console.error('Failed to generate PDF');
          alert('Failed to generate PDF. Please try again.');
        }
      } catch (error) {
        console.error('Error downloading PDF:', error);
        alert('Error downloading PDF. Please check your connection.');
      } finally {
        setIsDownloading(false);
      }
    };

    return (
      <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm">📋</span>
            </div>
            <div>
              <h4 className="font-medium text-blue-900">Event Plan PDF</h4>
              <p className="text-sm text-blue-700">
                {isDownloading ? 'Generating your plan...' : 'Comprehensive event plan ready for download'}
              </p>
            </div>
          </div>
          <button
            onClick={handleDownload}
            disabled={isDownloading}
            className={`px-4 py-2 ${
              isDownloading 
                ? 'bg-blue-300 cursor-not-allowed' 
                : 'bg-blue-500 hover:bg-blue-600'
            } text-white rounded-lg transition-colors flex items-center space-x-2`}
          >
            {isDownloading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <span>📄</span>
                <span>Download PDF</span>
              </>
            )}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className={`flex w-full mb-3 sm:mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Container for the bubble and its timestamp, controlling max width */}
      <div className={`max-w-[85%] sm:max-w-[70%] md:max-w-[65%] ${isUser ? 'ml-auto' : ''}`}>
        {/* Timestamp display */}
        {timestamp && (
          <div className={`text-xs ${isUser ? 'text-right' : 'text-left'} mb-0.5 px-1`}>
            <span className={isUser ? userTimestampClasses : aiTimestampClasses}>
              {timestamp}
            </span>
          </div>
        )}

        {/* Bubble content */}
        <div className={isUser ? userBubbleClasses : aiBubbleClasses}>
          {isGenerating ? (
            <TypingAnimation />
          ) : (
            <p className={isUser ? `text-white ${textBaseClasses}` : aiTextClasses}>
              {message}
            </p>
          )}

          {/* Images and music now only appear in gallery, not in chat */}

          {/* PDF Generation */}
          {!isUser && aiSuggestions?.pdf_requested && (
            <PDFDownloadSection chatId={chatId} />
          )}
        </div>
      </div>
    </div>
  );
}

ChatBubble.propTypes = {
  message: PropTypes.string.isRequired,
  isUser: PropTypes.bool.isRequired,
  timestamp: PropTypes.string,
  isGenerating: PropTypes.bool,
  aiSuggestions: PropTypes.object,
  chatId: PropTypes.string,
};