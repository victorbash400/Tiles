import PropTypes from 'prop-types';
import { motion } from 'framer-motion';

export default function ChatBubble({ message, isUser, timestamp, imageData, musicData, venueData, aiSuggestions }) {
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
          <p className={isUser ? `text-white ${textBaseClasses}` : aiTextClasses}>
            {message}
          </p>

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
  musicData: PropTypes.array,
  venueData: PropTypes.array,
  aiSuggestions: PropTypes.object,
};