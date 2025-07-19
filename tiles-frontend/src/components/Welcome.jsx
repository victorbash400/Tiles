import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import PropTypes from 'prop-types';

export default function Welcome({ onBegin }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 300);
    return () => clearTimeout(timer);
  }, []);

  const buttonVariants = {
    hidden: { opacity: 0, y: 32 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 1,
        ease: [0.25, 0.46, 0.45, 0.94],
      },
    },
  };

  const letterVariants = {
    initial: { y: 0 },
    animate: {
      y: [0, -5, 0, 5, 0],
      transition: {
        repeat: Infinity,
        duration: 4,
        ease: 'easeInOut',
      },
    },
  };

  const glassStyle =
    'w-14 h-14 sm:w-16 sm:h-16 flex items-center justify-center rounded-2xl text-white font-bold text-2xl sm:text-3xl backdrop-blur-xl bg-white/20 border border-white/40 shadow-[0_8px_32px_0_rgba(255,255,255,0.2)]';

  return (
    <div className="min-h-screen bg-[#EFDCCB] flex items-center justify-center relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 z-0">
        <img
          src="/blue.png"
          alt="Terrace Tiles"
          className="w-full h-full object-cover opacity-100"
        />
      </div>

      {/* Centered content wrapper */}
      <div className="relative z-10 flex flex-col items-center justify-center w-full" style={{ minHeight: '70vh' }}>
        {/* TILES glass effect */}
        <div className="flex justify-center items-center gap-4 mb-24">
          {'TILES'.split('').map((letter, i) => (
            <motion.div
              key={i}
              className={glassStyle}
              variants={letterVariants}
              initial="initial"
              animate="animate"
              style={{ animationDelay: `${i * 0.2}s` }}
            >
              {letter}
            </motion.div>
          ))}
        </div>

        {/* Button - moved lower */}
        <motion.button
          variants={buttonVariants}
          initial="hidden"
          animate={isVisible ? 'visible' : 'hidden'}
          onClick={onBegin}
          className="relative z-20 mt-20 px-10 py-4 backdrop-blur-3xl bg-white/20 border border-white/40 text-white rounded-full text-lg font-medium shadow-[0_8px_32px_0_rgba(255,255,255,0.2)] hover:shadow-2xl hover:bg-white/30 transition-all duration-300"
          whileHover={{ scale: 1.06 }}
          whileTap={{ scale: 0.95 }}
          style={{ fontFamily: 'system-ui, sans-serif' }}
        >
          <span className="flex items-center gap-2">
            <span>Ready to Create</span>
            <ArrowRight size={20} />
          </span>
        </motion.button>
      </div>
    </div>
  );
}

Welcome.propTypes = {
  onBegin: PropTypes.func.isRequired,
};
