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

  return (
    <div className="min-h-screen bg-[#EFDCCB] flex items-end justify-center relative overflow-hidden pb-24">
      {/* Background */}
      <div className="absolute inset-0 z-0">
        <img
          src="/TILES.png"
          alt="Terrace Tiles"
          className="w-full h-full object-cover opacity-100"
        />
      </div>

      {/* Only Button */}
      <motion.button
        variants={buttonVariants}
        initial="hidden"
        animate={isVisible ? 'visible' : 'hidden'}
        onClick={onBegin}
        className="relative z-20 px-10 py-4 backdrop-blur-3xl bg-white/20 border border-white/40 text-white rounded-full text-lg font-medium shadow-[0_8px_32px_0_rgba(255,255,255,0.2)] hover:shadow-2xl hover:bg-white/30 transition-all duration-300"
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
  );
}

Welcome.propTypes = {
  onBegin: PropTypes.func.isRequired,
};
