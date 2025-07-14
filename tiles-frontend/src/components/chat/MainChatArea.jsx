import { useEffect, useState, useRef } from 'react';
import PropTypes from 'prop-types';
import { Edit3, Search, Grid3X3, User, Settings, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import Card from './card';
import PlannerModal from './modal';
import FloatingTopbar from './FloatingTopbar';
import TilesLoadingAnimation from '../TilesLoadingAnimation';

export default function MainChatArea() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isAIModalOpen, setIsAIModalOpen] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    setLoading(true);
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';
      const response = await fetch(`${API_BASE_URL}/gallery/images`);
      if (!response.ok) throw new Error('Failed to fetch images');
      const data = await response.json();
      setImages(data.images || []);
    } catch (error) {
      console.error("Failed to fetch images", error);
      setImages([]);
    } finally {
      setLoading(false);
    }
  };

  const handlePlannerToggle = () => {
    setIsAIModalOpen(!isAIModalOpen);
  };

  const handleStyleSelect = async (style) => {
    console.log('Selected style:', style);
    setLoading(true);
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';
      const response = await fetch(`${API_BASE_URL}/gallery/search-style/${encodeURIComponent(style)}`);
      if (!response.ok) throw new Error('Failed to fetch style images');
      const data = await response.json();
      setImages(data.images || []);
    } catch (error) {
      console.error("Failed to fetch style images", error);
      setImages([]);
    } finally {
      setLoading(false);
    }
  };

  const handleMoodSelect = async (mood) => {
    console.log('Selected mood:', mood);
    setLoading(true);
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';
      const response = await fetch(`${API_BASE_URL}/gallery/search-style/${encodeURIComponent(mood)}`);
      if (!response.ok) throw new Error('Failed to fetch mood images');
      const data = await response.json();
      setImages(data.images || []);
    } catch (error) {
      console.error("Failed to fetch mood images", error);
      setImages([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Main Container with Elegant Backdrop */}
      <div className="flex-1 h-screen relative overflow-hidden">
        {/* Paper-like Background */}
        <div className="fixed inset-0 z-0 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-stone-100 via-stone-150/90 to-stone-200/80" style={{ backgroundColor: '#f7f5f3' }} />
          {images.length > 0 && (
            <div className="absolute inset-0 opacity-4">
              {images.slice(0, 3).map((img, index) => (
                <div
                  key={index}
                  className="absolute w-full h-full bg-cover bg-center"
                  style={{
                    backgroundImage: `url(${img.urls.regular})`,
                    filter: 'blur(50px) saturate(0.2) brightness(1.4) sepia(0.1)',
                    transform: `scale(1.1) rotate(${index * 15}deg)`,
                    opacity: 0.15 - index * 0.05,
                  }}
                />
              ))}
            </div>
          )}
        </div>
        
        {/* Decorative Glass Elements */}
        <div className="absolute top-20 right-20 w-32 h-32 rounded-2xl backdrop-blur-md bg-white/10 border border-white/20 shadow-inner shadow-white/10" />
        <div className="absolute bottom-32 left-16 w-24 h-24 rounded-full backdrop-blur-sm bg-amber-100/20 border border-amber-200/30" />
        <div className="absolute top-1/3 left-1/4 w-16 h-16 rounded-xl backdrop-blur-sm bg-white/15 border border-white/25" />

        {/* Floating Pill Topbar */}
        <FloatingTopbar 
          onStyleSelect={handleStyleSelect} 
          onMoodSelect={handleMoodSelect} 
          onReset={fetchImages} 
        />

        {/* Gallery Content */}
        <div className="flex-1 overflow-y-auto elegant-scrollbar relative z-20 pt-20" style={{ height: '100vh', maskImage: 'linear-gradient(to bottom, transparent 0%, black 6%, black 100%)' }}>
          {loading ? (
            <TilesLoadingAnimation />
          ) : (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="max-w-7xl mx-auto px-8 py-8"
            >
              <div className="columns-2 sm:columns-3 md:columns-4 lg:columns-4 gap-6">
                {images.map((img, index) => (
                  <motion.div 
                    key={img.id} 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: index * 0.05 }}
                    className="mb-6 break-inside-avoid group"
                  >
                    <div className="relative rounded-2xl p-2 shadow-lg hover:shadow-xl transition-all duration-500 overflow-hidden group glass-card">
                      {/* Glass background with color refraction */}
                      <div 
                        className="absolute inset-0 rounded-2xl opacity-20 group-hover:opacity-30 transition-opacity duration-500"
                        style={{
                          backgroundImage: `url(${img.urls.regular})`,
                          backgroundSize: 'cover',
                          backgroundPosition: 'center',
                          filter: 'blur(40px) saturate(2) brightness(1.3) contrast(1.2)',
                          transform: 'scale(1.2)',
                        }}
                      />
                      
                      {/* Glass layer with backdrop blur */}
                      <div className="absolute inset-0 backdrop-blur-md bg-white/25 border border-white/30 rounded-2xl shadow-inner shadow-white/20" />
                      
                      {/* Content layer */}
                      <div className="relative z-10">
                        <Card
                          image={img.urls?.regular}
                          aspectRatio={img.height / img.width}
                          type={img.type === 'playlist' || img.type === 'music_video' || img.platform === 'youtube' ? 'music' : img.type || 'image'}
                          data={(img.type === 'music' || img.type === 'playlist' || img.type === 'music_video' || img.platform === 'youtube') ? {
                            // Legacy fields
                            youtubeId: img.youtubeId,
                            appleMusicId: img.appleMusicId,
                            
                            // Enhanced playlist/video fields
                            playlistId: img.playlistId,
                            videoId: img.videoId,
                            type: img.type,
                            platform: img.platform,
                            embeddable: img.embeddable,
                            
                            // Content metadata
                            title: img.title,
                            artist: img.artist || img.channel,
                            channel: img.channel,
                            description: img.description,
                            duration: img.duration,
                            item_count: img.item_count,
                            published_at: img.published_at,
                            
                            // AI/Qloo metadata
                            confidence: img.confidence,
                            context_match: img.context_match,
                            qloo_ai_curated: img.qloo_ai_curated,
                            qloo_query: img.qloo_query,
                            qloo_data: img.qloo_data,
                            
                            // Images
                            thumbnail: img.urls?.regular,
                            thumbnail_url: img.thumbnail_url,
                            image_url: img.image_url,
                            
                            // Additional metadata
                            genre: img.genre,
                            mood: img.mood,
                            release_date: img.release_date
                          } : img.type === 'venue' ? {
                            name: img.name,
                            image: img.image,
                            address: img.address,
                            location: img.location,
                            business_rating: img.business_rating,
                            price_level: img.price_level,
                            phone: img.phone,
                            website: img.website,
                            is_open: img.is_open,
                            good_for: img.good_for,
                            features: img.features
                          } : img}
                        />
                        <div className="pt-3 px-2">
                          <h3 className="text-sm font-medium text-stone-900 truncate drop-shadow-sm">{img.user.name}</h3>
                          {img.alt_description && (
                            <p className="text-xs text-stone-700 mt-1 line-clamp-2 leading-relaxed opacity-90 drop-shadow-sm">
                              {img.alt_description}
                            </p>
                          )}
                        </div>
                      </div>
                      
                      {/* Edge highlight for realism */}
                      <div className="absolute inset-0 rounded-2xl border border-white/40 pointer-events-none" />
                    </div>
                  </motion.div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </motion.div>
          )}
        </div>

        {/* Floating Action Button - Enhanced with Sparkles icon */}
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 1, type: "spring", stiffness: 200 }}
          onClick={handlePlannerToggle}
          className="fixed bottom-8 right-8 z-40 w-12 h-12 rounded-full flex items-center justify-center group shadow-xl hover:shadow-2xl transition-all duration-300 border border-amber-200/40"
          style={{
            background: 'rgba(255, 255, 255, 0.18)',
            backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            boxShadow: '0 4px 24px 0 rgba(255, 193, 7, 0.10)',
          }}
          whileHover={{ scale: 1.08, rotate: 5 }}
          whileTap={{ scale: 0.95 }}
          title="Open Tiles"
        >
          <span className="absolute inset-0 rounded-full pointer-events-none" style={{
            background: 'linear-gradient(135deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0.10) 60%, rgba(255,255,255,0.18) 100%)',
            opacity: 0.7,
            zIndex: 1,
          }} />
          <Sparkles className="w-5 h-5 z-10 text-amber-700 group-hover:scale-110 group-hover:text-amber-900 transition-transform duration-200" />
        </motion.button>
      </div>

      <PlannerModal 
        isOpen={isAIModalOpen} 
        onClose={() => setIsAIModalOpen(false)}
        onGalleryRefresh={fetchImages}
      />

      <style jsx>{`
        .elegant-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .elegant-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .elegant-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(120, 113, 108, 0.3);
          border-radius: 8px;
          border: 2px solid transparent;
          background-clip: content-box;
        }
        .elegant-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(120, 113, 108, 0.5);
          background-clip: content-box;
        }

        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .glass-card {
          position: relative;
        }
        
        .glass-card::before {
          content: '';
          position: absolute;
          inset: -2px;
          background: linear-gradient(135deg, 
            rgba(255,255,255,0.4) 0%, 
            rgba(255,255,255,0.1) 25%, 
            rgba(255,255,255,0.05) 50%, 
            rgba(255,255,255,0.2) 100%
          );
          border-radius: 18px;
          z-index: -1;
          opacity: 0.6;
          filter: blur(1px);
        }
        
        .glass-card:hover::before {
          opacity: 0.8;
          background: linear-gradient(135deg, 
            rgba(255,255,255,0.5) 0%, 
            rgba(255,255,255,0.15) 25%, 
            rgba(255,255,255,0.08) 50%, 
            rgba(255,255,255,0.3) 100%
          );
        }
      `}</style>
    </>
  );
}

MainChatArea.propTypes = {
  // No props needed anymore
};