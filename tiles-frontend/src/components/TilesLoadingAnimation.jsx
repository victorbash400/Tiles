import React from 'react';
import { motion } from 'framer-motion';

const TilesLoadingAnimation = () => {
  return (
    <motion.div 
      className="absolute inset-0 z-50 flex items-center justify-center"
      animate={{
        background: [
          'radial-gradient(circle at 20% 30%, #F59E0B 0%, #FED7AA 25%, #FEF3C7 50%, #FFFBEB 75%, #F3F4F6 100%)',
          'radial-gradient(circle at 80% 60%, #FBBF24 0%, #F59E0B 25%, #FED7AA 50%, #FEF3C7 75%, #FFFBEB 100%)',
          'radial-gradient(circle at 40% 80%, #FED7AA 0%, #FFFBEB 25%, #F59E0B 50%, #FBBF24 75%, #FEF3C7 100%)',
          'radial-gradient(circle at 70% 20%, #FEF3C7 0%, #FBBF24 25%, #F59E0B 50%, #FED7AA 75%, #FFFBEB 100%)',
          'radial-gradient(circle at 30% 70%, #FFFBEB 0%, #FEF3C7 25%, #FED7AA 50%, #F59E0B 75%, #FBBF24 100%)',
          'radial-gradient(circle at 20% 30%, #F59E0B 0%, #FED7AA 25%, #FEF3C7 50%, #FFFBEB 75%, #F3F4F6 100%)'
        ]
      }}
      transition={{
        duration: 8,
        repeat: Infinity,
        ease: 'easeInOut'
      }}
    >
      {/* Text */}
      <motion.div
        className="text-center space-y-2"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: 'easeOut' }}
      >
        <motion.div
          className="text-3xl text-stone-800 font-bold tracking-wide"
          style={{ 
            fontFamily: 'Pacifico, cursive',
            textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
          }}
          animate={{ opacity: [0.8, 1, 0.8] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        >
          Crafting your vibe...
        </motion.div>
        <motion.div
          className="text-sm text-stone-600 font-medium"
          style={{ textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)' }}
          animate={{ opacity: [0.6, 0.9, 0.6] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut', delay: 0.3 }}
        >
          Making something gorgeous
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

export default TilesLoadingAnimation;
