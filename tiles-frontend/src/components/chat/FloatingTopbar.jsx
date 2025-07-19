import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { Bell, Settings } from 'lucide-react';

export default function FloatingTopbar({ onStyleSelect, onMoodSelect, onReset }) {
  return (
    <>
      {/* Brand Logo - Separate from topbar */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        className="fixed top-6 left-8 z-30 text-4xl font-pacifico text-amber-600 drop-shadow-lg tiles-brand-text"
        style={{ fontFamily: 'Pacifico, cursive !important', fontWeight: 'normal !important' }}
      >
        Tiles
      </motion.div>

      {/* Pointless icons for visual balance - they don't do anything but look pretty */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="fixed top-6 right-8 z-30 flex items-center gap-3"
      >
        {/* Notification icon - completely pointless but adds visual balance */}
        <motion.button
          whileHover={{ scale: 1.1, rotate: 5 }}
          whileTap={{ scale: 0.95 }}
          className="w-10 h-10 bg-white/20 backdrop-blur-xl border border-white/30 rounded-full flex items-center justify-center text-amber-600 hover:bg-white/30 transition-all duration-300 shadow-lg"
          title="Notifications (does nothing)"
        >
          <Bell className="w-5 h-5" />
        </motion.button>
        
        {/* Settings icon - equally pointless but aesthetically pleasing */}
        <motion.button
          whileHover={{ scale: 1.1, rotate: -5 }}
          whileTap={{ scale: 0.95 }}
          className="w-10 h-10 bg-white/20 backdrop-blur-xl border border-white/30 rounded-full flex items-center justify-center text-amber-600 hover:bg-white/30 transition-all duration-300 shadow-lg"
          title="Settings (also does nothing)"
        >
          <Settings className="w-5 h-5" />
        </motion.button>
      </motion.div>

      {/* Topbar */}
      <div className="fixed top-6 left-1/2 transform -translate-x-1/2 z-30 group">
        <motion.div
          initial={{ opacity: 0, y: -20, scale: 0.8 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          className="bg-white/25 backdrop-blur-xl border border-white/40 shadow-xl"
          whileHover={{
            borderRadius: '56px',
            padding: '24px 32px',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
          }}
          style={{
            borderRadius: '9999px',
            padding: '12px 24px',
            transformOrigin: 'center'
          }}
          transition={{
            duration: 0.6, 
            ease: [0.16, 1, 0.3, 1],
            type: 'spring',
            stiffness: 300,
            damping: 30,
            mass: 0.8
          }}
        >
          {/* Collapsed State */}
          <motion.div 
            className="flex items-center gap-2 group-hover:hidden"
          >
            {[
              { icon: '🎂', text: 'Birthday', color: 'from-pink-100 to-pink-200 hover:from-pink-200 hover:to-pink-300' },
              { icon: '💍', text: 'Wedding', color: 'from-rose-100 to-rose-200 hover:from-rose-200 hover:to-rose-300' },
              { icon: '🎓', text: 'Graduation', color: 'from-blue-100 to-blue-200 hover:from-blue-200 hover:to-blue-300' },
              { icon: '🎄', text: 'Holiday', color: 'from-green-100 to-green-200 hover:from-green-200 hover:to-green-300' },
              { icon: '🎵', text: 'Music', color: 'from-purple-100 to-purple-200 hover:from-purple-200 hover:to-purple-300' },
            ].map((style, index) => (
              <motion.button
                key={style.text}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className={`flex items-center gap-1.5 px-3 py-2 bg-gradient-to-r ${style.color} backdrop-blur-sm border border-white/40 rounded-full text-stone-700 hover:text-stone-800 transition-all duration-300 shadow-sm hover:shadow-md font-medium text-xs`}
                onClick={() => onStyleSelect(style.text === 'Birthday' ? 'Birthday Party' : 
                                           style.text === 'Holiday' ? 'Holiday Party' :
                                           style.text === 'Music' ? 'Music Festival' : style.text)}
              >
                <span className="text-sm">{style.icon}</span>
                <span>{style.text}</span>
              </motion.button>
            ))}
          </motion.div>

          {/* Expanded State */}
          <motion.div 
            className="hidden group-hover:block space-y-3"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ 
              duration: 0.4, 
              ease: [0.16, 1, 0.3, 1],
              delay: 0.1
            }}
          >
            {/* Main Events Row */}
            <div className="flex flex-wrap justify-center gap-2">
              {[
                { icon: '🎂', text: 'Birthday', color: 'from-pink-100 to-pink-200 hover:from-pink-200 hover:to-pink-300', size: 'large' },
                { icon: '💍', text: 'Wedding', color: 'from-rose-100 to-rose-200 hover:from-rose-200 hover:to-rose-300', size: 'large' },
                { icon: '🎓', text: 'Graduation', color: 'from-blue-100 to-blue-200 hover:from-blue-200 hover:to-blue-300', size: 'medium' },
                { icon: '🎄', text: 'Holiday', color: 'from-green-100 to-green-200 hover:from-green-200 hover:to-green-300', size: 'medium' },
                { icon: '🏖️', text: 'Summer', color: 'from-cyan-100 to-cyan-200 hover:from-cyan-200 hover:to-cyan-300', size: 'small' },
                { icon: '🎵', text: 'Music', color: 'from-purple-100 to-purple-200 hover:from-purple-200 hover:to-purple-300', size: 'small' },
                { icon: '🍷', text: 'Wine', color: 'from-amber-100 to-amber-200 hover:from-amber-200 hover:to-amber-300', size: 'small' },
                { icon: '🌙', text: 'Date', color: 'from-indigo-100 to-indigo-200 hover:from-indigo-200 hover:to-indigo-300', size: 'small' },
              ].map((style, index) => {
                const sizeClasses = {
                  large: 'px-4 py-2.5 text-sm',
                  medium: 'px-3 py-2 text-xs', 
                  small: 'px-2.5 py-1.5 text-xs'
                };
                const iconSizes = {
                  large: 'text-base',
                  medium: 'text-sm',
                  small: 'text-sm'
                };
                return (
                  <motion.button
                    key={style.text}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ 
                      delay: index * 0.05,
                      duration: 0.3,
                      ease: [0.16, 1, 0.3, 1]
                    }}
                    whileHover={{ 
                      scale: 1.05,
                      transition: { type: 'spring', stiffness: 400, damping: 20 }
                    }}
                    whileTap={{ scale: 0.95 }}
                    className={`flex items-center gap-1.5 ${sizeClasses[style.size]} bg-gradient-to-r ${style.color} backdrop-blur-sm border border-white/40 rounded-full text-stone-700 hover:text-stone-800 shadow-sm hover:shadow-md font-medium`}
                    onClick={() => onStyleSelect(style.text === 'Birthday' ? 'Birthday Party' : 
                                               style.text === 'Holiday' ? 'Holiday Party' :
                                               style.text === 'Summer' ? 'Summer Vibes' :
                                               style.text === 'Music' ? 'Music Festival' :
                                               style.text === 'Wine' ? 'Wine Tasting' :
                                               style.text === 'Date' ? 'Date Night' : style.text)}
                  >
                    <span className={iconSizes[style.size]}>{style.icon}</span>
                    <span>{style.text}</span>
                  </motion.button>
                );
              })}
            </div>
            {/* Moods Row */}
            <div className="flex flex-wrap justify-center gap-2">
              {[
                { icon: '✨', text: 'Minimalist', color: 'from-stone-100 to-stone-200', size: 'medium' },
                { icon: '🌈', text: 'Vibrant', color: 'from-orange-100 to-yellow-200', size: 'small' },
                { icon: '🌿', text: 'Bohemian', color: 'from-emerald-100 to-teal-200', size: 'medium' },
                { icon: '💎', text: 'Luxury', color: 'from-violet-100 to-purple-200', size: 'small' },
                { icon: '🌸', text: 'Romantic', color: 'from-pink-100 to-rose-200', size: 'medium' },
                { icon: '⚡', text: 'Energetic', color: 'from-yellow-100 to-orange-200', size: 'small' },
                { icon: '🔄', text: 'Reload', color: 'from-gray-100 to-gray-200', size: 'small', isReset: true },
              ].map((mood, index) => {
                const sizeClasses = {
                  medium: 'px-3 py-1.5 text-xs',
                  small: 'px-2.5 py-1 text-xs'
                };
                const iconSizes = {
                  medium: 'text-sm',
                  small: 'text-xs'
                };
                return (
                  <motion.button
                    key={mood.text}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ 
                      delay: (index + 8) * 0.05,
                      duration: 0.3,
                      ease: [0.16, 1, 0.3, 1]
                    }}
                    whileHover={{ 
                      scale: 1.05,
                      transition: { type: 'spring', stiffness: 400, damping: 20 }
                    }}
                    whileTap={{ scale: 0.95 }}
                    className={`flex items-center gap-1 ${sizeClasses[mood.size]} bg-gradient-to-r ${mood.color} hover:shadow-md backdrop-blur-sm border border-white/30 rounded-full text-stone-600 hover:text-stone-700 font-medium`}
                    onClick={mood.isReset ? onReset : () => onMoodSelect(mood.text)}
                  >
                    <span className={iconSizes[mood.size]}>{mood.icon}</span>
                    <span>{mood.text}</span>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        </motion.div>
      </div>
    </>
  );
}

// Add CSS to ensure Pacifico font is applied
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    .tiles-brand-text {
      font-family: 'Pacifico', cursive !important;
      font-weight: normal !important;
    }
  `;
  if (!document.head.querySelector('style[data-tiles-brand]')) {
    style.setAttribute('data-tiles-brand', 'true');
    document.head.appendChild(style);
  }
}

FloatingTopbar.propTypes = {
  onStyleSelect: PropTypes.func.isRequired,
  onMoodSelect: PropTypes.func.isRequired,
  onReset: PropTypes.func.isRequired,
};