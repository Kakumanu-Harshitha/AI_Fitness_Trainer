import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  MessageSquare, 
  X, 
  Send, 
  Brain, 
  Maximize2,
  ChevronUp,
  User
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import GlassCard from './GlassCard';
import { useApi } from '../hooks/useApi';

const AiAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm your Lifestyle AI. How can I help you today?" }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { post } = useApi();
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await post('/chatbot/ask', { message: userMessage });
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I'm having trouble connecting right now." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsOpen(true)}
          className="w-14 h-14 bg-gradient-to-tr from-primary to-lime-400 rounded-full shadow-lg shadow-primary/30 flex items-center justify-center text-black"
        >
          <Brain size={28} />
        </motion.button>
      )}

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            className="absolute top-16 right-0 w-[90vw] max-w-sm h-[60vh] flex flex-col shadow-2xl rounded-2xl overflow-hidden"
          >
            <div className="flex-1 flex flex-col bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl border border-zinc-200 dark:border-zinc-800 rounded-2xl overflow-hidden transition-colors duration-300">
              {/* Header */}
              <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-gray-50/50 dark:bg-zinc-950/50 transition-colors duration-300">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                    <Brain size={18} />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 dark:text-white text-sm transition-colors duration-300">Lifestyle AI</h3>
                    <div className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                      <span className="text-[10px] text-gray-500 dark:text-zinc-400 uppercase tracking-wider transition-colors duration-300">Online</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button 
                    onClick={() => setIsOpen(false)}
                    className="p-2 text-gray-400 dark:text-zinc-400 hover:text-gray-900 dark:hover:text-white transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-zinc-800"
                  >
                    <X size={18} />
                  </button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, idx) => (
                  <div 
                    key={idx} 
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div 
                      className={`max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed transition-colors duration-300 ${
                        msg.role === 'user' 
                          ? 'bg-primary text-black rounded-tr-sm font-medium' 
                          : 'bg-gray-100 dark:bg-zinc-800/80 text-gray-800 dark:text-zinc-200 rounded-tl-sm border border-gray-200 dark:border-zinc-700/50'
                      }`}
                    >
                      {msg.content}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 dark:bg-zinc-800/50 p-3 rounded-2xl rounded-tl-sm border border-gray-200 dark:border-zinc-700/50 flex gap-1 transition-colors duration-300">
                      <span className="w-1.5 h-1.5 bg-gray-500 dark:bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                      <span className="w-1.5 h-1.5 bg-gray-500 dark:bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      <span className="w-1.5 h-1.5 bg-gray-500 dark:bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-3 border-t border-zinc-200 dark:border-zinc-800 bg-gray-50/50 dark:bg-zinc-950/30 transition-colors duration-300">
                <div className="flex items-center gap-2 bg-white dark:bg-zinc-900/50 p-1.5 rounded-xl border border-zinc-200 dark:border-zinc-800 focus-within:border-primary/50 transition-colors duration-300">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask about diet, workout..."
                    className="flex-1 bg-transparent text-gray-900 dark:text-white text-sm p-2 focus:outline-none placeholder-gray-400 dark:placeholder-zinc-600 transition-colors duration-300"
                    disabled={loading}
                  />
                  <button 
                    onClick={handleSend}
                    disabled={!input.trim() || loading}
                    className="p-2 bg-primary text-black rounded-lg hover:bg-primary/90 transition-all disabled:opacity-50 disabled:bg-gray-200 dark:disabled:bg-zinc-800 disabled:text-gray-400 dark:disabled:text-zinc-600"
                  >
                    <Send size={16} />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default AiAssistant;
