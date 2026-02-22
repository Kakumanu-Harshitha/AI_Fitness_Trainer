import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send } from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { useApi } from '../hooks/useApi';
import { WS_URL, API_BASE_URL } from '../utils/api';
import GlassCard from '../components/GlassCard';

const Chat = () => {
  const { username } = useParams();
  const navigate = useNavigate();
  const { user, token } = useApp();
  const { get } = useApi();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(true);
  const [friend, setFriend] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const connectWebSocket = () => {
    if (ws.current && (ws.current.readyState === WebSocket.OPEN || ws.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const identifier = token || user?.username || localStorage.getItem('userToken') || 'anonymous';
    const socketUrl = `${WS_URL}/api/v1/ws?token=${identifier}`;
    
    console.log('[Chat] Connecting to WebSocket:', socketUrl);
    ws.current = new WebSocket(socketUrl);

    ws.current.onopen = () => {
      console.log('[Chat] Connected');
      setIsConnected(true);
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('[Chat] Received message:', data);
        
        // Handle incoming chat messages
        if (data.type === 'chat_received' && data.from === username) {
          setMessages(prev => [...prev, {
            id: Date.now(),
            sender_id: friend?.id,
            content: data.message, // Map 'message' from websocket to 'content'
            timestamp: data.timestamp || new Date().toISOString()
          }]);
        }
      } catch (e) {
        console.warn('[Chat] Failed to parse message:', event.data);
      }
    };

    ws.current.onclose = (e) => {
      console.log('[Chat] Disconnected:', e.code, e.reason);
      setIsConnected(false);
      
      // Don't reconnect if it was a normal closure (e.g. component unmount)
      if (e.code !== 1000) {
        console.log('[Chat] Attempting to reconnect in 3s...');
        reconnectTimeout.current = setTimeout(connectWebSocket, 3000);
      }
    };

    ws.current.onerror = (err) => {
      console.error('[Chat] WebSocket error:', err);
    };
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchFriendAndHistory = async () => {
      try {
        setLoading(true);
        // Fetch friend details first (to get their ID/avatar)
        const users = await get(`/social/users/search?q=${username}`);
        const foundFriend = users.find(u => u.username === username);
        setFriend(foundFriend);

        // Fetch history
        const history = await get(`/social/chat/history/${username}`);
        setMessages(history);
      } catch (error) {
        console.error('Failed to load chat:', error);
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchFriendAndHistory();
      connectWebSocket();
    }

    return () => {
      if (ws.current) {
        ws.current.close(1000, 'Component unmounting');
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, [username, token, user, get]);

  const handleSend = () => {
    if (!inputText.trim()) return;

    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      console.error('[Chat] Cannot send: WebSocket not connected');
      // Optionally try to reconnect
      connectWebSocket();
      return;
    }

    const payload = {
      type: 'chat_message',
      target_username: username,
      message: inputText.trim()
    };

    try {
      ws.current.send(JSON.stringify(payload));

      // Optimistically add to UI
      setMessages(prev => [...prev, {
        id: Date.now(),
        sender_id: user.id,
        content: inputText.trim(), // Use 'content' to match history format
        timestamp: new Date().toISOString()
      }]);

      setInputText('');
    } catch (err) {
      console.error('[Chat] Failed to send message:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] max-w-4xl mx-auto text-gray-900 dark:text-white transition-colors duration-300">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button 
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-gray-100 dark:hover:bg-white/10 rounded-full transition-colors text-gray-500 dark:text-zinc-400"
        >
          <ArrowLeft size={24} />
        </button>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-zinc-800 flex items-center justify-center text-xl overflow-hidden">
            {friend?.profile_image ? (
              <img 
                src={`${API_BASE_URL}${friend.profile_image}`}
                alt={username}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.parentElement.innerHTML = '👤';
                }}
              />
            ) : (
              '👤'
            )}
          </div>
          <div>
            <h1 className="text-xl font-black">{username}</h1>
            <p className="text-xs text-gray-500 dark:text-zinc-500 uppercase font-black tracking-widest">
              {isConnected ? 'Active Now' : 'Connecting...'}
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <GlassCard className="flex-1 overflow-y-auto p-4 mb-4 flex flex-col gap-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-zinc-500 gap-2">
            <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-zinc-900 flex items-center justify-center text-3xl mb-2">
              💬
            </div>
            <p className="font-bold">No messages yet</p>
            <p className="text-sm">Start the conversation with {username}!</p>
          </div>
        ) : (
          messages.map((msg) => {
            const isMe = msg.sender_id === user.id;
            return (
              <div 
                key={msg.id}
                className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] px-4 py-2 rounded-2xl ${
                  isMe 
                    ? 'bg-primary text-black font-medium rounded-tr-none' 
                    : 'bg-gray-200 dark:bg-zinc-800 text-gray-900 dark:text-white rounded-tl-none'
                }`}>
                  <p>{msg.content}</p>
                  <p className={`text-[10px] mt-1 opacity-50 ${isMe ? 'text-black' : 'text-gray-500 dark:text-zinc-400'}`}>
                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </GlassCard>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type a message..."
          className="flex-1 bg-white dark:bg-zinc-900 border border-gray-200 dark:border-white/10 rounded-xl px-4 py-3 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors"
        />
        <button
          onClick={handleSend}
          disabled={!inputText.trim()}
          className="bg-primary text-black p-3 rounded-xl hover:scale-105 active:scale-95 transition-transform disabled:opacity-50 disabled:hover:scale-100"
        >
          <Send size={24} />
        </button>
      </div>
    </div>
  );
};

export default Chat;
