import PropTypes from 'prop-types';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, Music, MapPin, Calendar, ExternalLink, Phone, Globe, Star, Clock, Users, CreditCard, Utensils, CheckCircle, Circle, ChefHat, Volume2, VolumeX, Maximize2, List, User } from 'lucide-react';

export default function Card({ image, aspectRatio, type = 'image', data = {} }) {
  // Limit aspect ratio for more consistent, smaller cards
  const limitedAspectRatio = Math.min(Math.max(aspectRatio, 0.7), 1.8);
  
  // State for embedded player
  const [isPlaying, setIsPlaying] = useState(false);
  const [showEmbed, setShowEmbed] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const renderContent = () => {
    switch (type) {
      case 'music':
        return (
          <div className="relative overflow-hidden rounded-xl">
            {!showEmbed ? (
              // Music Card Preview
              <div className="w-full bg-gradient-to-br from-purple-100 to-pink-100 p-4">
                <div className="flex items-center gap-3">
                  {/* Album/Playlist Art */}
                  <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0 relative">
                    {data.thumbnail_url || data.image_url || data.thumbnail ? (
                      <img 
                        src={data.thumbnail_url || data.image_url || data.thumbnail} 
                        alt={data.title} 
                        className="w-full h-full object-cover" 
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-purple-200 to-pink-200 flex items-center justify-center">
                        {data.type === 'playlist' ? (
                          <List className="w-6 h-6 text-purple-600" />
                        ) : (
                          <Music className="w-6 h-6 text-purple-600" />
                        )}
                      </div>
                    )}
                    
                    {/* Type indicator */}
                    {data.type === 'playlist' && (
                      <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-purple-600 rounded-full flex items-center justify-center">
                        <List className="w-3 h-3 text-white" />
                      </div>
                    )}
                  </div>
                  
                  {/* Music Info */}
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm text-stone-800 truncate">
                      {data.title || 'Music Title'}
                    </h4>
                    <div className="flex items-center gap-2 text-xs mt-1">
                      {data.channel && (
                        <div className="flex items-center gap-1 text-stone-600">
                          <User className="w-3 h-3" />
                          <span className="truncate">{data.channel}</span>
                        </div>
                      )}
                      {data.item_count && (
                        <span className="text-purple-600 bg-purple-200 px-2 py-0.5 rounded-full">
                          {data.item_count} songs
                        </span>
                      )}
                    </div>
                    
                    {/* Additional metadata */}
                    <div className="flex items-center gap-2 text-xs mt-1">
                      {data.type && (
                        <span className="capitalize text-purple-600">
                          {data.type === 'music_video' ? 'Video' : data.type}
                        </span>
                      )}
                      {data.platform && (
                        <span className="text-stone-500 capitalize">{data.platform}</span>
                      )}
                      {data.duration && (
                        <span className="text-stone-500">{data.duration}</span>
                      )}
                    </div>
                  </div>
                  
                  {/* Playback Controls */}
                  <div className="flex gap-1">
                    {/* Embedded Play Button */}
                    {(data.playlistId || data.videoId || data.youtubeId) && data.embeddable !== false && (
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          setShowEmbed(true);
                          setIsPlaying(false); // Start paused, user can click play
                        }}
                        className="w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors shadow-sm"
                        title="Play Embedded"
                      >
                        <Play className="w-4 h-4 ml-0.5" />
                      </motion.button>
                    )}
                    
                    {/* YouTube Link Button */}
                    {(data.playlistId || data.videoId || data.youtubeId) && (
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          const id = data.playlistId || data.videoId || data.youtubeId;
                          const url = data.playlistId 
                            ? `https://www.youtube.com/playlist?list=${data.playlistId}`
                            : `https://www.youtube.com/watch?v=${id}`;
                          window.open(url, '_blank');
                        }}
                        className="w-8 h-8 bg-red-100 text-red-600 rounded-full flex items-center justify-center hover:bg-red-200 transition-colors"
                        title="Open in YouTube"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </motion.button>
                    )}
                    
                    {/* Spotify Link (if available) */}
                    {data.qloo_data?.external?.spotify?.id && (
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          window.open(`https://open.spotify.com/album/${data.qloo_data.external.spotify.id}`, '_blank');
                        }}
                        className="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center hover:bg-green-200 transition-colors"
                        title="Open in Spotify"
                      >
                        <Music className="w-4 h-4" />
                      </motion.button>
                    )}
                  </div>
                </div>
                
                {/* AI Confidence & Context Match */}
                <div className="mt-3 space-y-2">
                  {data.confidence && (
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-purple-200 rounded-full h-1.5">
                        <div 
                          className="bg-purple-500 h-1.5 rounded-full transition-all duration-500"
                          style={{ width: `${data.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-purple-600">{Math.round(data.confidence * 100)}% confidence</span>
                    </div>
                  )}
                  
                  {data.context_match && (
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-pink-200 rounded-full h-1.5">
                        <div 
                          className="bg-pink-500 h-1.5 rounded-full transition-all duration-500"
                          style={{ width: `${data.context_match * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-pink-600">{Math.round(data.context_match * 100)}% match</span>
                    </div>
                  )}
                  
                  {/* Qloo AI indicator */}
                  {data.qloo_ai_curated && (
                    <div className="flex items-center gap-2 text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded-full">
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
                      <span>Qloo AI Curated</span>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              // Embedded Player
              <div className="w-full bg-black rounded-xl overflow-hidden">
                {/* Player Controls Header */}
                <div className="bg-stone-900 p-3 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsPlaying(!isPlaying);
                        // Force reload iframe with autoplay when playing
                        if (!isPlaying) {
                          const iframe = document.querySelector(`iframe[title="${data.title}"]`);
                          if (iframe) {
                            const currentSrc = iframe.src;
                            iframe.src = currentSrc.includes('autoplay=') 
                              ? currentSrc.replace(/autoplay=\d/, 'autoplay=1')
                              : currentSrc + '&autoplay=1';
                          }
                        }
                      }}
                      className="w-6 h-6 bg-red-600 rounded-full flex items-center justify-center hover:bg-red-700 transition-colors"
                    >
                      {isPlaying ? (
                        <Pause className="w-3 h-3 text-white" />
                      ) : (
                        <Play className="w-3 h-3 text-white ml-0.5" />
                      )}
                    </motion.button>
                    <span className="text-white text-sm font-medium truncate">
                      {data.title}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {/* Expand/Collapse */}
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsExpanded(!isExpanded);
                      }}
                      className="w-6 h-6 bg-stone-700 text-stone-300 rounded flex items-center justify-center hover:bg-stone-600 transition-colors"
                      title="Toggle Size"
                    >
                      <Maximize2 className="w-3 h-3" />
                    </motion.button>
                    
                    {/* Close Player */}
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowEmbed(false);
                        setIsPlaying(false);
                      }}
                      className="w-6 h-6 bg-stone-700 text-stone-300 rounded flex items-center justify-center hover:bg-stone-600 transition-colors"
                      title="Close Player"
                    >
                      ×
                    </motion.button>
                  </div>
                </div>
                
                {/* YouTube Embed */}
                <div className={`relative ${isExpanded ? 'h-80' : 'h-48'} transition-all duration-300`}>
                  <iframe
                    width="100%"
                    height="100%"
                    src={
                      data.playlistId 
                        ? `https://www.youtube.com/embed/videoseries?list=${data.playlistId}&enablejsapi=1&autoplay=${isPlaying ? 1 : 0}&rel=0&modestbranding=1&controls=1&showinfo=0&origin=${window.location.origin}`
                        : `https://www.youtube.com/embed/${data.videoId || data.youtubeId}?enablejsapi=1&autoplay=${isPlaying ? 1 : 0}&rel=0&modestbranding=1&controls=1&showinfo=0&origin=${window.location.origin}`
                    }
                    title={data.title}
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    allowFullScreen
                    referrerPolicy="strict-origin-when-cross-origin"
                    className="rounded-b-xl"
                  />
                  
                  {/* Player status overlay */}
                  <div className="absolute top-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                    {data.type === 'playlist' ? `Playlist (${data.item_count || 0} songs)` : 'Video'}
                  </div>
                </div>
              </div>
            )}
          </div>
        );

      case 'video':
        return (
          <div className="relative overflow-hidden rounded-xl">
            {/* Video thumbnail */}
            <div className="w-full bg-gradient-to-br from-red-100 to-red-200" 
                 style={{ aspectRatio: limitedAspectRatio ? `1 / ${limitedAspectRatio}` : '16/9' }}>
              {data.thumbnail ? (
                <img src={data.thumbnail} alt={data.title} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Play className="w-16 h-16 text-red-600" />
                </div>
              )}
            </div>
            {/* Video play button */}
            <div className="absolute inset-0 flex items-center justify-center">
              <motion.div 
                whileHover={{ scale: 1.1 }}
                className="w-16 h-16 bg-red-500/95 border border-red-400/50 rounded-full flex items-center justify-center shadow-sm"
              >
                <Play className="w-8 h-8 text-white ml-1" />
              </motion.div>
            </div>
            {/* Video info */}
            <div className="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm p-3">
              <h4 className="font-medium text-sm text-stone-800 truncate">{data.title || 'Video Title'}</h4>
              <p className="text-xs text-stone-600 truncate">{data.channel || 'Channel Name'}</p>
            </div>
          </div>
        );

      case 'venue':
        return (
          <div className="relative overflow-hidden rounded-xl bg-white shadow-lg">
            {/* Large Venue Image */}
            <div className="w-full h-48 overflow-hidden">
              {data.image ? (
                <img 
                  src={data.image} 
                  alt={data.name} 
                  className="w-full h-full object-cover hover:scale-105 transition-transform duration-300" 
                />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-emerald-100 to-teal-200 flex items-center justify-center">
                  <MapPin className="w-16 h-16 text-emerald-600" />
                </div>
              )}
            </div>
            
            {/* Compact Info Section */}
            <div className="p-4 space-y-3">
              {/* Venue Name & Rating */}
              <div className="flex items-start justify-between">
                <h4 className="font-semibold text-sm text-stone-900 leading-tight flex-1 pr-2">
                  {data.name || 'Venue Name'}
                </h4>
                {data.business_rating && (
                  <div className="flex items-center gap-1 text-amber-600 bg-amber-50 px-2 py-1 rounded-full">
                    <Star className="w-3 h-3 fill-current" />
                    <span className="text-xs font-medium">{data.business_rating}</span>
                  </div>
                )}
              </div>
              
              {/* Location & Price */}
              <div className="space-y-1">
                <p className="text-xs text-stone-600 flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-stone-400" />
                  <span className="truncate">{data.address || data.location || 'Location'}</span>
                </p>
                
                <div className="flex items-center justify-between">
                  {data.price_level && (
                    <div className="flex items-center gap-1 text-green-600">
                      <CreditCard className="w-3 h-3" />
                      <span className="text-xs font-medium">{'$'.repeat(data.price_level)}</span>
                    </div>
                  )}
                  
                  {data.is_open !== undefined && (
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${data.is_open ? 'bg-green-500' : 'bg-red-500'}`} />
                      <span className={`text-xs ${data.is_open ? 'text-green-600' : 'text-red-600'}`}>
                        {data.is_open ? 'Open' : 'Closed'}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="flex gap-2 pt-2">
                {data.phone && (
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(`tel:${data.phone}`, '_self');
                    }}
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-emerald-100 text-emerald-700 rounded-lg text-xs font-medium hover:bg-emerald-200 transition-colors"
                  >
                    <Phone className="w-3 h-3" />
                    Call
                  </motion.button>
                )}
                {data.website && (
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(data.website, '_blank');
                    }}
                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-blue-100 text-blue-700 rounded-lg text-xs font-medium hover:bg-blue-200 transition-colors"
                  >
                    <Globe className="w-3 h-3" />
                    Visit
                  </motion.button>
                )}
              </div>
            </div>
          </div>
        );

      case 'event':
        return (
          <div className="relative overflow-hidden rounded-xl">
            {/* Event image */}
            <div className="w-full" style={{ aspectRatio: limitedAspectRatio ? `1 / ${limitedAspectRatio}` : 'auto' }}>
              {data.image ? (
                <img src={data.image} alt={data.title} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-32 bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                  <Calendar className="w-12 h-12 text-blue-600" />
                </div>
              )}
            </div>
            {/* Event info */}
            <div className="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm p-3">
              <h4 className="font-medium text-sm text-stone-800 truncate">{data.title || 'Event Title'}</h4>
              <p className="text-xs text-stone-600 truncate flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {data.date || 'Date TBD'}
              </p>
              <p className="text-xs text-stone-600 truncate flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                {data.location || 'Location TBD'}
              </p>
            </div>
          </div>
        );

      case 'restaurant':
        return (
          <div className="relative overflow-hidden rounded-xl">
            <div className="w-full bg-gradient-to-br from-orange-50 to-red-100 p-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0">
                  {data.image ? (
                    <img src={data.image} alt={data.name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-orange-200 to-red-200 flex items-center justify-center">
                      <Utensils className="w-6 h-6 text-orange-600" />
                    </div>
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-sm text-stone-800 truncate">{data.name || 'Restaurant Name'}</h4>
                  <div className="flex items-center gap-2 text-xs mt-1">
                    {data.business_rating && (
                      <div className="flex items-center gap-1 text-amber-600">
                        <Star className="w-3 h-3 fill-current" />
                        <span>{data.business_rating}</span>
                      </div>
                    )}
                    {data.price_level && (
                      <span className="text-green-600">{'$'.repeat(data.price_level)}</span>
                    )}
                    {data.cuisine && (
                      <span className="text-orange-600">{data.cuisine}</span>
                    )}
                  </div>
                </div>
                
                <div className="flex gap-1">
                  {data.phone && (
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        window.open(`tel:${data.phone}`, '_self');
                      }}
                      className="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center hover:bg-green-200 transition-colors"
                      title="Call Restaurant"
                    >
                      <Phone className="w-4 h-4" />
                    </motion.button>
                  )}
                  {data.website && (
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        window.open(data.website, '_blank');
                      }}
                      className="w-8 h-8 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center hover:bg-orange-200 transition-colors"
                      title="View Menu"
                    >
                      <Utensils className="w-4 h-4" />
                    </motion.button>
                  )}
                </div>
              </div>
              
              {data.good_for && data.good_for.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {data.good_for.slice(0, 2).map((feature, idx) => (
                    <span key={idx} className="text-xs bg-orange-100 text-orange-800 px-2 py-0.5 rounded-full">
                      {feature.name || feature}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        );

      case 'checklist':
        return (
          <div className="relative overflow-hidden rounded-xl">
            <div className="w-full bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <h4 className="font-medium text-sm text-stone-800">{data.title || 'Event Checklist'}</h4>
              </div>
              
              <div className="space-y-2">
                {data.items && data.items.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs">
                    {item.completed ? (
                      <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
                    ) : (
                      <Circle className="w-4 h-4 text-stone-400 flex-shrink-0" />
                    )}
                    <span className={`${item.completed ? 'text-green-700 line-through' : 'text-stone-700'} truncate`}>
                      {item.text}
                    </span>
                    {item.count && (
                      <span className="text-xs text-blue-600 bg-blue-100 px-1.5 py-0.5 rounded-full ml-auto flex-shrink-0">
                        {item.count}
                      </span>
                    )}
                  </div>
                ))}
              </div>
              
              {data.progress !== undefined && (
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs text-stone-600 mb-1">
                    <span>Progress</span>
                    <span>{Math.round(data.progress * 100)}%</span>
                  </div>
                  <div className="w-full bg-stone-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${data.progress * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        );

      default: // 'image'
        return image ? (
          <div className="overflow-hidden rounded-xl">
            <motion.img
              src={image}
              className="w-full object-cover"
              loading="lazy"
              style={{
                aspectRatio: limitedAspectRatio ? `1 / ${limitedAspectRatio}` : 'auto'
              }}
            />
          </div>
        ) : null;
    }
  };

  return (
    <motion.div 
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className="break-inside-avoid cursor-pointer group overflow-hidden rounded-xl"
    >
      {renderContent()}
      
      {/* External link indicator for interactive content */}
      {(type === 'music' || type === 'video') && (
        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="w-6 h-6 bg-white/95 border border-stone-200 rounded-full flex items-center justify-center shadow-sm">
            <ExternalLink className="w-3 h-3 text-stone-500" />
          </div>
        </div>
      )}
    </motion.div>
  );
}

Card.propTypes = {
  image: PropTypes.string,
  aspectRatio: PropTypes.number,
  type: PropTypes.oneOf(['image', 'music', 'video', 'venue', 'event', 'restaurant', 'checklist']),
  data: PropTypes.object,
};