import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageCircle, X } from 'lucide-react';
import GlassCard from './GlassCard';

const NotificationToast = () => {
  const [notification, setNotification] = useState(null);
  const [visible, setVisible] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleNotification = (e) => {
      const { detail } = e;
      setNotification(detail);
      setVisible(true);

      // Auto hide after 4 seconds
      const timer = setTimeout(() => {
        setVisible(false);
      }, 4000);
      return () => clearTimeout(timer);
    };

    window.addEventListener('new-notification', handleNotification);
    return () => window.removeEventListener('new-notification', handleNotification);
  }, []);

  const handleClick = () => {
    if (notification?.type === 'message' && notification?.title) {
      navigate(`/chat/${notification.title}`);
      setVisible(false);
    }
  };

  if (!visible || !notification) return null;

  return (
    <div 
      onClick={handleClick}
      className="fixed top-24 right-4 z-50 animate-in slide-in-from-right duration-300 cursor-pointer"
    >
      <GlassCard className="p-4 border-primary/50 flex items-start gap-3 w-80 shadow-lg shadow-primary/10 bg-white/90 dark:bg-zinc-900/90 hover:bg-gray-50 dark:hover:bg-zinc-800/80 transition-colors duration-300">
        <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
          <MessageCircle size={20} className="text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start">
            <h4 className="font-bold text-sm text-gray-900 dark:text-white truncate transition-colors duration-300">{notification.title}</h4>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                setVisible(false);
              }}
              className="text-gray-500 hover:text-gray-900 dark:text-zinc-500 dark:hover:text-white transition-colors duration-300"
            >
              <X size={14} />
            </button>
          </div>
          <p className="text-xs text-gray-600 dark:text-zinc-400 mt-1 line-clamp-2 transition-colors duration-300">{notification.message}</p>
        </div>
      </GlassCard>
    </div>
  );
};

export default NotificationToast;
