import PropTypes from 'prop-types';
import { motion } from 'framer-motion';

export default function ChatBubble({ message, isUser, timestamp, imageData, musicData, venueData, aiSuggestions, isGenerating }) {
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

  // AI Generation Animation Component
  const GenerationAnimation = () => (
    <div className="flex items-center space-x-2 py-2">
      <div className="flex items-center space-x-1">
        <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse"></div>
        <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
      </div>
      <div className="text-sm text-stone-600 animate-pulse">
        <span className="font-medium">AI is generating your recommendations...</span>
      </div>
    </div>
  );

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
            <GenerationAnimation />
          ) : (
            <p className={isUser ? `text-white ${textBaseClasses}` : aiTextClasses}>
              {message}
            </p>
          )}

          {/* AI-generated images */}
          {!isUser && imageData && imageData.length > 0 && (
            <div className="mt-4 space-y-3">
              <div className="text-xs text-stone-600 font-medium">✨ Visual Inspiration</div>
              <div className="grid grid-cols-2 gap-2">
                {imageData.slice(0, 4).map((img, index) => (
                  <motion.div
                    key={img.id || index}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="relative group overflow-hidden rounded-xl"
                  >
                    <img
                      src={img.urls?.regular || img.urls?.small}
                      alt={img.alt_description || 'Event inspiration'}
                      className="w-full h-24 object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent group-hover:from-black/30 transition-colors duration-300" />
                  </motion.div>
                ))}
              </div>
              {imageData.length > 4 && (
                <div className="text-xs text-stone-500 text-center">
                  +{imageData.length - 4} more images
                </div>
              )}
            </div>
          )}

          {/* AI-generated music */}
          {!isUser && musicData && musicData.length > 0 && (
            <div className="mt-4 space-y-3">
              <div className="text-xs text-stone-600 font-medium">🎵 Music Recommendations</div>
              <div className="space-y-2">
                {musicData.slice(0, 3).map((music, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="flex items-center gap-3 p-2 rounded-lg bg-stone-50 border border-stone-200"
                  >
                    <div className="w-2 h-2 bg-amber-500 rounded-full"></div>
                    <div className="flex-1">
                      <div className="text-xs font-medium text-stone-800">{music.title}</div>
                      <div className="text-xs text-stone-600">{music.artist}</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* PDF Generation */}
          {!isUser && aiSuggestions?.pdf_requested && (
            <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">📋</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-blue-900">Event Plan PDF</h4>
                    <p className="text-sm text-blue-700">Comprehensive event plan ready for download</p>
                  </div>
                </div>
                <button
                  onClick={async () => {
                    try {
                      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';
                      const chatId = new URLSearchParams(window.location.search).get('chatId') || 'default';
                      
                      const response = await fetch(`${API_BASE_URL}/generate-pdf/${chatId}`, {
                        method: 'POST'
                      });
                      
                      if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `event_plan_${chatId}.pdf`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(a);
                      } else {
                        console.error('Failed to generate PDF');
                      }
                    } catch (error) {
                      console.error('Error downloading PDF:', error);
                    }
                  }}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center space-x-2"
                >
                  <span>📄</span>
                  <span>Download PDF</span>
                </button>
              </div>
            </div>
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
  imageData: PropTypes.array,
  isGenerating: PropTypes.bool,
  musicData: PropTypes.array,
  venueData: PropTypes.array,
  aiSuggestions: PropTypes.object,
};