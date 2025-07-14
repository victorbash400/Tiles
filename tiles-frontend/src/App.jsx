import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import MainChatArea from './components/chat/MainChatArea';
import Welcome from './components/Welcome';

function App() {
  const [showWelcome, setShowWelcome] = useState(true);

  const handleBegin = () => {
    console.log('handleBegin called!');
    setShowWelcome(false);
  };

  console.log('App render - showWelcome:', showWelcome);

  return (
    <div className="w-full h-screen overflow-hidden">
      <AnimatePresence mode="wait">
        {showWelcome ? (
          <motion.div
            key="welcome"
            initial={{ opacity: 1 }}
            exit={{ 
              opacity: 0,
              scale: 0.95,
              transition: { duration: 0.5, ease: "easeInOut" }
            }}
          >
            <Welcome onBegin={handleBegin} />
          </motion.div>
        ) : (
          <motion.div 
            key="main-app" 
            className="w-full h-screen bg-stone-50"
            initial={{ 
              opacity: 0,
              scale: 1.05 
            }}
            animate={{ 
              opacity: 1,
              scale: 1,
              transition: { duration: 0.6, ease: "easeOut" }
            }}
          >
            <MainChatArea />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;