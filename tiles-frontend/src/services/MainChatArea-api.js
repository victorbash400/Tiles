// MainChatArea-api.js
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

// Generate a simple 9-character chat ID
export const generateChatId = () => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < 9; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

// Chat API functions
export const createNewChat = async () => {
  const chatId = generateChatId();
  const response = await fetch(`${API_BASE_URL}/chats`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      chatId,
      title: 'New Chat',
      createdAt: new Date().toISOString(),
      messages: []
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to create new chat');
  }

  const data = await response.json();
  return { chatId, ...data };
};

export const getAllChats = async () => {
  const response = await fetch(`${API_BASE_URL}/chats`);

  if (!response.ok) {
    throw new Error('Failed to fetch chats');
  }

  const data = await response.json();
  return data;
};

export const getChatById = async (chatId) => {
  const response = await fetch(`${API_BASE_URL}/chats/${chatId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch chat');
  }

  const data = await response.json();
  return data;
};

export const saveMessage = async (chatId, messageContent, userSession = null) => {
  const response = await fetch(`${API_BASE_URL}/chats/${chatId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      content: messageContent,
      user_session: userSession 
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to save message or get AI response');
  }

  const data = await response.json();
  console.log('saveMessage API response:', data);
  return data;
};

export const getAIMemory = async (userSession = null) => {
  const url = userSession ? `${API_BASE_URL}/ai/memory?user_session=${userSession}` : `${API_BASE_URL}/ai/memory`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Failed to fetch AI memory');
  }

  const data = await response.json();
  return data;
};

// Gallery API functions
export const fetchGalleryImages = async () => {
  const response = await fetch(`${API_BASE_URL}/gallery/images`);

  if (!response.ok) {
    throw new Error('Failed to fetch gallery images');
  }

  const data = await response.json();
  return data.images || [];
};

export const fetchImagesByOrientation = async (orientation, count = 12) => {
  const response = await fetch(`${API_BASE_URL}/gallery/images/${orientation}?count=${count}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch ${orientation} images`);
  }

  const data = await response.json();
  return data.images || [];
};

export const searchImages = async (query, count = 12, orientation = null) => {
  let url = `${API_BASE_URL}/gallery/search?query=${encodeURIComponent(query)}&count=${count}`;
  
  if (orientation) {
    url += `&orientation=${orientation}`;
  }

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Failed to search images');
  }

  const data = await response.json();
  return data.images || [];
};