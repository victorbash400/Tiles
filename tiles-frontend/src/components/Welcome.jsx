import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import PropTypes from 'prop-types';

export default function Welcome({ onBegin }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 300);

    if (typeof document !== 'undefined') {
      const style = document.createElement('style');
      style.textContent = `
        .welcome-tiles-text {
          font-family: 'Pacifico', cursive !important;
          font-weight: normal !important;
        }
      `;
      if (!document.head.querySelector('style[data-welcome-tiles]')) {
        style.setAttribute('data-welcome-tiles', 'true');
        document.head.appendChild(style);
      }
    }

    return () => clearTimeout(timer);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 1.2,
        ease: [0.25, 0.46, 0.45, 0.94],
        staggerChildren: 0.2,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 32 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.9,
        ease: [0.25, 0.46, 0.45, 0.94],
      },
    },
  };

  return (
    <div className="min-h-screen bg-[#EFDCCB] flex flex-col items-center justify-center px-6 md:px-10 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 z-0">
        <img
          src="/black.jpg"
          alt="Elegant terrace backdrop"
          className="w-full h-full object-cover opacity-90"
        />
      </div>

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/30 to-black/60 z-10" />

      {/* Glass Decorations */}
      <div className="absolute top-10 left-10 w-40 h-40 rounded-3xl backdrop-blur-md bg-white/10 border border-white/20 z-20 shadow-inner shadow-white/10" />
      <div className="absolute bottom-12 right-12 w-56 h-56 rounded-[4rem] backdrop-blur-lg bg-white/15 border border-white/25 z-20 shadow-inner shadow-white/10" />
      <div className="absolute top-[35%] right-[25%] w-32 h-32 rounded-full backdrop-blur-sm bg-white/10 border border-white/15 z-20 shadow-inner shadow-white/10" />

      {/* Main Content */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate={isVisible ? 'visible' : 'hidden'}
        className="relative z-30 text-center max-w-2xl w-full"
      >
        <motion.h1
          variants={itemVariants}
          className="text-4xl md:text-5xl font-semibold text-white drop-shadow-xl leading-tight md:leading-snug"
          style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif' }}
        >
          Welcome to
          <br />
          <span
            className="font-pacifico text-amber-200 welcome-tiles-text"
            style={{ fontFamily: 'Pacifico, cursive', fontWeight: 'normal' }}
          >
            Tiles
          </span>
        </motion.h1>

        <motion.p
          variants={itemVariants}
          className="text-lg md:text-xl mt-6 md:mt-8 text-white/90 font-normal tracking-wide max-w-xl mx-auto"
          style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif' }}
        >
          a warm, playful canvas for designing life’s little (and big) moments.
        </motion.p>

        <motion.button
          variants={itemVariants}
          onClick={onBegin}
          className="mt-10 px-8 py-3 backdrop-blur-xl bg-white/30 border border-white/40 text-white rounded-full text-base font-medium shadow-xl hover:shadow-2xl transition-all duration-300 hover:bg-white/40 hover:border-white/60"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif' }}
        >
          <span className="flex items-center gap-2">
            <span>Let's Create</span>
            <ArrowRight size={18} />
          </span>
        </motion.button>
      </motion.div>
    </div>
  );
}

Welcome.propTypes = {
  onBegin: PropTypes.func.isRequired,
};
