import React, { useState, useEffect, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, Plus, BookOpen, Loader } from 'lucide-react';

// Custom scrollbar styles
const scrollbarStyles = `
  .custom-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: rgba(251, 191, 36, 0.3) transparent;
  }
  
  .custom-scrollbar::-webkit-scrollbar {
    width: 6px;
  }
  
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
  
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: rgba(251, 191, 36, 0.3);
    border-radius: 3px;
    transition: background-color 0.2s ease;
  }
  
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background-color: rgba(251, 191, 36, 0.5);
  }
  
  .custom-scrollbar::-webkit-scrollbar-corner {
    background: transparent;
  }
`;

import {
  getChatById,
  saveMessage,
  createNewChat,
  getAIMemory,
} from '../../services/MainChatArea-api';
import ChatInput from './ChatInput';
import ChatBubble from './ChatBubble';

export default function PlannerModal({ isOpen, onClose, onGalleryRefresh, onChatSessionChange, initialChatId }) {
  // Inject custom scrollbar styles
  useEffect(() => {
    const styleElement = document.createElement('style');
    styleElement.textContent = scrollbarStyles;
    document.head.appendChild(styleElement);
    
    return () => {
      document.head.removeChild(styleElement);
    };
  }, []);
  const [activeView, setActiveView] = useState('chat');
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(initialChatId);

  // **NEW**: Sync with parent when initialChatId changes (keeps modal in sync)
  useEffect(() => {
    console.log('🔍 MODAL SYNC DEBUG:');
    console.log('   initialChatId prop:', initialChatId, 'Type:', typeof initialChatId);
    console.log('   currentChatId state:', currentChatId, 'Type:', typeof currentChatId);
    console.log('   Are they different?', initialChatId !== currentChatId);
    
    if (initialChatId !== currentChatId) {
      console.log('🔄 Modal syncing with parent chat ID:', initialChatId);
      setCurrentChatId(initialChatId);
    }
  }, [initialChatId, currentChatId]);
  const [messages, setMessages] = useState([]);
  const [aiMemory, setAiMemory] = useState(null);
  const [loading, setLoading] = useState({ chats: false, messages: false, memory: false });
  const [isNewChat, setIsNewChat] = useState(!initialChatId);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadAllChats = useCallback(async () => {
    setLoading(prev => ({ ...prev, chats: true }));
    try {
      // Only load current chat for sidebar, not all chats from all sessions
      if (currentChatId) {
        const currentChat = await getChatById(currentChatId);
        setChats([currentChat]);
      } else {
        // No current chat - start fresh
        setChats([]);
        setIsNewChat(true);
      }
    } catch (err) {
      console.error('Error loading current chat:', err);
      setChats([]);
    } finally {
      setLoading(prev => ({ ...prev, chats: false }));
    }
  }, [currentChatId]);

  const loadAIMemory = useCallback(async () => {
    setLoading(prev => ({ ...prev, memory: true }));
    try {
      const memory = await getAIMemory();
      setAiMemory(memory);
    } catch (err) {
      console.error('Error loading AI memory:', err);
    } finally {
      setLoading(prev => ({ ...prev, memory: false }));
    }
  }, []);

  // **NEW**: Only handle keyboard events and view setting on open/close
  useEffect(() => {
    const escHandler = (e) => e.key === 'Escape' && onClose();
    if (isOpen) {
      document.addEventListener('keydown', escHandler);
      setActiveView('chat');
    }
    return () => document.removeEventListener('keydown', escHandler);
  }, [isOpen, onClose]);

  // **NEW**: Separate initialization - only run once or when chat changes
  useEffect(() => {
    if (currentChatId) {
      loadAllChats();
      loadAIMemory();
    }
  }, [currentChatId, loadAllChats, loadAIMemory]);

  // **NEW**: Load messages only when chat changes, not when modal opens/closes
  useEffect(() => {
    if (currentChatId) {
      const loadChat = async () => {
        setLoading(prev => ({ ...prev, messages: true }));
        try {
          const chat = await getChatById(currentChatId);
          setMessages(chat.messages || []);
          setIsNewChat(chat.messages?.length === 0);
          console.log('💬 Loaded chat messages for session:', currentChatId, '- Message count:', chat.messages?.length || 0);
        } catch (err) {
          console.error('Chat error:', err);
          setMessages([]);
          setIsNewChat(true);
        } finally {
          setLoading(prev => ({ ...prev, messages: false }));
        }
      };
      loadChat();
    } else {
      // No chat ID - reset to new chat state
      setMessages([]);
      setIsNewChat(true);
    }
  }, [currentChatId]); // **REMOVED isOpen dependency**

  const handleCreateNewChat = async () => {
    setLoading(prev => ({ ...prev, messages: true }));
    try {
      const newChat = await createNewChat();
      setChats(prev => [newChat, ...prev.filter(chat => chat.chatId !== newChat.chatId)]);
      setCurrentChatId(newChat.chatId);
      setMessages([]);
      setIsNewChat(true);
      setActiveView('chat');
      // Notify parent about new chat session
      if (onChatSessionChange) {
        console.log('🔍 NEW CHAT CREATION - Calling onChatSessionChange with:', newChat.chatId, 'Type:', typeof newChat.chatId);
        onChatSessionChange(newChat.chatId);
      }
      return newChat.chatId;
    } catch (err) {
      console.error('New chat error:', err);
      return null;
    } finally {
      setLoading(prev => ({ ...prev, messages: false }));
    }
  };

  const handleSendMessage = async (text) => {
    console.log('🔍 MODAL DEBUG - handleSendMessage START');
    console.log('🔍 currentChatId state:', currentChatId, 'Type:', typeof currentChatId);
    console.log('🔍 initialChatId prop:', initialChatId, 'Type:', typeof initialChatId);
    
    let chatId = currentChatId;
    console.log('🔍 chatId variable initial:', chatId, 'Type:', typeof chatId);
    
    if (!chatId) {
      console.log('🔍 No chatId, creating new chat...');
      const newChatId = await handleCreateNewChat();
      if (!newChatId) return;
      chatId = newChatId;
      console.log('🔍 chatId after creation:', chatId, 'Type:', typeof chatId);
      // Update currentChatId to ensure it's in sync
      setCurrentChatId(chatId);
    }

    const userMessage = {
      id: Date.now().toString(),
      content: text,
      role: 'user',
      timestamp: new Date().toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit', hour12: false}),
      message_type: 'text',
    };

    setMessages(prev => [...prev, userMessage]);
    setIsNewChat(false);

    // Add AI generation animation
    const loadingMessage = {
      id: `loading-${Date.now()}`,
      content: '',
      role: 'assistant',
      timestamp: new Date().toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit', hour12: false}),
      message_type: 'loading',
      isGenerating: true
    };

    setMessages(prev => [...prev, loadingMessage]);

    try {
      console.log('🔍 BEFORE API CALL - chatId about to send:', chatId, 'Type:', typeof chatId);
      console.log('💬 Sending message to chat ID:', chatId);
      const aiResponse = await saveMessage(chatId, text);
      console.log('🔄 AI Response received:', aiResponse);
      console.log('🔍 AI suggestions structure:', aiResponse?.ai_suggestions);
      console.log('🔍 Refresh gallery flag:', aiResponse?.ai_suggestions?.refresh_gallery);
      console.log('🔍 DEBUGGING: aiResponse exists:', !!aiResponse);
      console.log('🔍 DEBUGGING: ai_suggestions exists:', !!aiResponse?.ai_suggestions);
      
      // Always remove loading message first
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.id !== loadingMessage.id);
        console.log('🗑️ Removed loading message, remaining messages:', filtered.length);
        return filtered;
      });
      
      if (aiResponse) {
        // Add AI response
        setMessages(prev => {
          const updated = [...prev, aiResponse];
          console.log('➕ Added AI response, total messages:', updated.length);
          return updated;
        });
        
        loadAIMemory();
        
        // **AUTOMATIC REFRESH**: Check if we need to refresh the gallery
        const shouldRefresh = aiResponse.ai_suggestions?.refresh_gallery;
        const hasGeneratedContent = aiResponse.image_data?.length > 0 || aiResponse.music_data?.length > 0 || 
                                   aiResponse.venue_data?.length > 0 || aiResponse.food_data?.length > 0;
        
        if (shouldRefresh || hasGeneratedContent) {
          console.log('🖼️ Gallery refresh needed!');
          console.log('   Explicit refresh flag:', shouldRefresh);
          console.log('   Has generated content:', hasGeneratedContent);
          console.log('   Images:', aiResponse.image_data?.length || 0);
          console.log('   Music:', aiResponse.music_data?.length || 0);
          console.log('   Venues:', aiResponse.venue_data?.length || 0);
          console.log('   Food:', aiResponse.food_data?.length || 0);
          
          if (onGalleryRefresh) {
            // Attempt automatic refresh
            console.log('🔄 ATTEMPTING automatic gallery refresh...');
            setTimeout(() => {
              onGalleryRefresh(chatId);
              
              // **ULTIMATE FALLBACK**: Set a secondary timer to check if refresh worked
              // If not, we'll trigger the manual refresh button as a last resort
              setTimeout(() => {
                console.log('🔍 FALLBACK CHECK: Verifying gallery refresh success...');
                // This fallback ensures gallery updates even if automatic refresh has issues
                if (onGalleryRefresh) {
                  console.log('🔄 SAFETY FALLBACK: Re-triggering gallery refresh...');
                  onGalleryRefresh(chatId);
                }
              }, 2000); // Give 2 seconds for automatic refresh to work
            }, 100);
          } else {
            console.error('❌ onGalleryRefresh callback is missing!');
          }
        } else {
          console.log('📋 No gallery refresh needed - no content generated');
        }
      } else {
        console.error('❌ AI Response is null or undefined');
      }
    } catch (err) {
      console.error('💥 Message error:', err);
      console.error('💥 Error details:', err.message);
      
      // **CORS ERROR FALLBACK**: Still try to refresh gallery since content might have been generated
      if (err.message?.includes('CORS') || err.message?.includes('Failed to fetch')) {
        console.log('🔄 CORS ERROR: Attempting fallback gallery refresh...');
        if (onGalleryRefresh) {
          setTimeout(() => {
            console.log('🔄 CORS FALLBACK: Executing gallery refresh...');
            onGalleryRefresh(chatId);
            
            // Double fallback for CORS errors - try again after delay
            setTimeout(() => {
              console.log('🔄 CORS DOUBLE FALLBACK: Re-attempting gallery refresh...');
              onGalleryRefresh(chatId);
            }, 2000);
          }, 1000);
        }
      }
      
      // Remove both user and loading messages on error
      setMessages(prev => prev.filter(msg => 
        msg.id !== userMessage.id && msg.id !== loadingMessage.id
      ));
    }
  };

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0, 0, 0, 0.4)' }}
      onClick={onClose}
    >
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 20, opacity: 0 }}
        transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-5xl h-[85vh] flex flex-col overflow-hidden"
        style={{
          background: 'rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderRadius: '24px',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.1)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4" style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{
              background: 'rgba(251, 191, 36, 0.15)',
              backdropFilter: 'blur(10px)'
            }}>
              <Sparkles className="w-5 h-5 text-amber-700" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-amber-700" style={{ 
                fontFamily: 'Pacifico, cursive',
                textShadow: '0 2px 4px rgba(0, 0, 0, 0.2)'
              }}>Tiles</h2>
              <p className="text-sm text-stone-700" style={{
                textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
              }}>Warm, minimal, intentional</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveView('chat')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeView === 'chat'
                  ? 'text-amber-800 shadow-sm'
                  : 'text-stone-600 hover:text-stone-800'
              }`}
              style={activeView === 'chat' ? {
                background: 'rgba(251, 191, 36, 0.15)',
                backdropFilter: 'blur(10px)'
              } : {}}
            >
              Chat
            </button>
            <button
              onClick={() => setActiveView('memory')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeView === 'memory'
                  ? 'text-amber-800 shadow-sm'
                  : 'text-stone-600 hover:text-stone-800'
              }`}
              style={activeView === 'memory' ? {
                background: 'rgba(251, 191, 36, 0.15)',
                backdropFilter: 'blur(10px)'
              } : {}}
            >
              Memory
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-xl flex items-center justify-center text-stone-600 hover:text-stone-800 transition-all duration-200"
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(10px)'
              }}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="flex-1 flex overflow-hidden relative">
          <AnimatePresence mode="wait">
            {activeView === 'chat' ? (
              <motion.div
                key="chat-view"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                className="flex w-full h-full"
              >
                <div className="w-1/5 p-3 flex flex-col" style={{
                  borderRight: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <button
                    onClick={handleCreateNewChat}
                    className="w-full text-amber-900 hover:text-amber-950 rounded-xl py-2 px-2 text-sm font-medium mb-3 transition-all duration-200 hover:scale-105"
                    style={{
                      background: 'rgba(251, 191, 36, 0.25)',
                      backdropFilter: 'blur(15px)',
                      border: '1px solid rgba(251, 191, 36, 0.3)',
                      textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                    }}
                  >
                    + New
                  </button>
                  <div className="flex-1 overflow-y-auto space-y-2 custom-scrollbar">
                    {loading.chats ? (
                      <div className="flex items-center justify-center py-8 text-stone-700" style={{
                        textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                      }}>
                        <Loader className="w-4 h-4 animate-spin mr-2" />
                        Loading chats...
                      </div>
                    ) : chats.length === 0 ? (
                      <div className="text-center py-8 text-stone-600" style={{
                        textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                      }}>
                        <p className="text-sm">No chats yet</p>
                        <p className="text-xs mt-1">Start a new conversation above</p>
                      </div>
                    ) : (
                      chats.map(chat => (
                        <button
                          key={chat.chatId}
                          onClick={() => {
                            setCurrentChatId(chat.chatId);
                            const selectedChat = chats.find(c => c.chatId === chat.chatId);
                            setIsNewChat(selectedChat?.messages?.length === 0);
                          }}
                          className={`w-full text-left px-2 py-1.5 rounded-lg text-xs transition-all duration-200 ${
                            currentChatId === chat.chatId ? 'font-semibold text-stone-900' : 'text-stone-700 hover:text-stone-900'
                          }`}
                          style={{
                            ...(currentChatId === chat.chatId ? {
                              background: 'rgba(255, 255, 255, 0.25)',
                              backdropFilter: 'blur(15px)',
                              border: '1px solid rgba(255, 255, 255, 0.2)'
                            } : {}),
                            textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                          }}
                        >
                          <div className="font-medium truncate text-xs">
                            {chat.title || 'Chat'}
                          </div>
                          {chat.messages?.length > 0 && (
                            <div className="text-xs text-stone-600 mt-0.5 truncate" style={{
                              textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                            }}>
                              {chat.messages[chat.messages.length - 1]?.content.substring(0, 20)}...
                            </div>
                          )}
                        </button>
                      ))
                    )}
                  </div>
                </div>

                <div className="flex-1 flex flex-col overflow-hidden" style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  backdropFilter: 'blur(10px)'
                }}>
                  <div className="flex-1 overflow-y-auto space-y-4 custom-scrollbar" style={{
                    padding: '24px',
                    paddingBottom: '120px'
                  }}>
                    {loading.messages ? (
                      <div className="flex justify-center items-center h-full text-stone-700" style={{
                        textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                      }}>
                        <Loader className="w-6 h-6 animate-spin mr-2" />
                        Loading messages...
                      </div>
                    ) : messages.length === 0 ? (
                      <div className="flex flex-col items-center justify-center h-full text-center">
                        <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4" style={{
                          background: 'linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(251, 191, 36, 0.1) 100%)',
                          backdropFilter: 'blur(10px)'
                        }}>
                          <Sparkles className="w-8 h-8 text-amber-700" />
                        </div>
                        <h3 className="text-lg font-medium text-stone-900 mb-2" style={{
                          textShadow: '0 2px 4px rgba(0, 0, 0, 0.15)'
                        }}>
                          {isNewChat ? 'Let\'s craft the perfect atmosphere' : 'Welcome back!'}
                        </h3>
                        <p className="text-stone-700 max-w-sm mb-4" style={{
                          textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                        }}>
                          {isNewChat
                            ? 'What vision are you bringing to life? Describe your event and let\'s make it unforgettable.'
                            : 'Ready to continue crafting your perfect event?'}
                        </p>
                        
                        {/* Show prominent Start Chat button if no active chat */}
                        {!currentChatId && (
                          <button
                            onClick={handleCreateNewChat}
                            disabled={loading.messages}
                            className="flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                            style={{
                              background: 'linear-gradient(135deg, rgba(251, 191, 36, 0.9) 0%, rgba(217, 119, 6, 0.9) 100%)',
                              backdropFilter: 'blur(15px)',
                              border: '1px solid rgba(251, 191, 36, 0.4)',
                              color: 'white',
                              textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)',
                              boxShadow: '0 4px 12px rgba(251, 191, 36, 0.3)'
                            }}
                          >
                            {loading.messages ? (
                              <>
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                <span>Starting...</span>
                              </>
                            ) : (
                              <>
                                <Plus className="w-4 h-4" />
                                <span>Start New Chat</span>
                              </>
                            )}
                          </button>
                        )}
                      </div>
                    ) : (
                      <>
                        {messages.map(msg => (
                          <ChatBubble
                            key={msg.id}
                            message={msg.content}
                            isUser={msg.role === 'user'}
                            timestamp={msg.timestamp}
                            aiSuggestions={msg.ai_suggestions}
                            isGenerating={msg.isGenerating}
                            chatId={currentChatId}
                          />
                        ))}
                        <div ref={messagesEndRef} />
                      </>
                    )}
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="memory-view"
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                className="w-full h-full overflow-y-auto px-6 py-8 custom-scrollbar"
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  backdropFilter: 'blur(10px)'
                }}
              >
                <div className="max-w-3xl mx-auto">
                  <div className="flex items-center gap-3 mb-8">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{
                      background: 'rgba(251, 191, 36, 0.15)',
                      backdropFilter: 'blur(10px)'
                    }}>
                      <BookOpen className="w-5 h-5 text-amber-700" />
                    </div>
                    <h2 className="text-xl font-semibold text-stone-900" style={{
                      textShadow: '0 2px 4px rgba(0, 0, 0, 0.15)'
                    }}>Planning Memory</h2>
                  </div>
                  {loading.memory ? (
                    <div className="flex items-center justify-center py-12 text-stone-700" style={{
                      textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                    }}>
                      <Loader className="w-5 h-5 animate-spin mr-2" />
                      Loading memory...
                    </div>
                  ) : aiMemory ? (
                    <div className="space-y-6">
                      <div className="rounded-xl p-4 shadow-sm" style={{
                        background: 'rgba(255, 255, 255, 0.1)',
                        backdropFilter: 'blur(15px)',
                        border: '1px solid rgba(255, 255, 255, 0.15)'
                      }}>
                        <h3 className="text-sm font-semibold text-stone-900 mb-1" style={{
                          textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                        }}>Summary</h3>
                        <p className="text-sm text-stone-800 leading-relaxed" style={{
                          textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                        }}>
                          {aiMemory?.summary || 'No summary available yet. Keep chatting to generate insights.'}
                        </p>
                      </div>
                      {aiMemory?.active_monitoring?.length > 0 && (
                        <div className="rounded-xl p-4 shadow-sm" style={{
                          background: 'rgba(255, 255, 255, 0.1)',
                          backdropFilter: 'blur(15px)',
                          border: '1px solid rgba(255, 255, 255, 0.15)'
                        }}>
                          <h3 className="text-sm font-semibold text-stone-900 mb-2" style={{
                            textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                          }}>Active Projects</h3>
                          <div className="flex flex-wrap gap-2">
                            {aiMemory.active_monitoring.map((topic, idx) => (
                              <span
                                key={idx}
                                className="text-amber-900 text-xs px-3 py-1 rounded-full transition-all duration-200"
                                style={{
                                  background: 'rgba(251, 191, 36, 0.25)',
                                  backdropFilter: 'blur(15px)',
                                  border: '1px solid rgba(251, 191, 36, 0.3)',
                                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                                }}
                              >
                                {topic}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-stone-600" style={{
                      textShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
                    }}>
                      <BookOpen className="w-12 h-12 mx-auto mb-4 opacity-60" />
                      <p className="text-sm">No memory data available yet</p>
                      <p className="text-xs mt-1">Start chatting to build your AI memory</p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          {/* Floating ChatInput - only show in chat view */}
          {activeView === 'chat' && (
            <div className="absolute bottom-4 left-1/5 right-4 z-10">
              <ChatInput
                onSendMessage={handleSendMessage}
                hasMessages={messages.length > 0}
                hasActiveChat={!!currentChatId}
              />
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

PlannerModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onGalleryRefresh: PropTypes.func,
};
