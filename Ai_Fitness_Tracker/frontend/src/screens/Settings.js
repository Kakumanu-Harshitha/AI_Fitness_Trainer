import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Bell, 
  Moon, 
  Shield, 
  HelpCircle, 
  LogOut, 
  ChevronRight,
  Volume2,
  Lock
} from 'lucide-react';
import GlassCard from '../components/GlassCard';
import { useApp } from '../contexts/AppContext';

const Settings = () => {
  const navigate = useNavigate();
  const { logout, settings, updateSettings } = useApp();
  const [notifications, setNotifications] = useState(true);
  const [sound, setSound] = useState(true);
  
  const darkMode = settings.theme === 'dark';

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      await logout();
      navigate('/login');
    }
  };

  const SettingItem = ({ icon: Icon, label, value, type = 'toggle', onClick }) => (
    <div 
      className="flex items-center justify-between p-4 hover:bg-black/5 dark:hover:bg-white/5 rounded-xl transition-colors cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-full bg-zinc-100 dark:bg-zinc-900 flex items-center justify-center text-zinc-500 dark:text-zinc-400">
          <Icon size={20} />
        </div>
        <span className="font-bold text-zinc-800 dark:text-zinc-200">{label}</span>
      </div>
      
      {type === 'toggle' ? (
        <div 
          className={`w-12 h-6 rounded-full p-1 transition-colors duration-300 ${
            value ? 'bg-primary' : 'bg-zinc-300 dark:bg-zinc-800'
          }`}
        >
          <div 
            className={`w-4 h-4 rounded-full bg-white shadow-sm transition-transform duration-300 ${
              value ? 'translate-x-6' : 'translate-x-0'
            }`}
          />
        </div>
      ) : (
        <ChevronRight size={20} className="text-zinc-400 dark:text-zinc-600" />
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-white dark:bg-black text-black dark:text-white p-6 pb-24 max-w-2xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <button 
          onClick={() => navigate(-1)}
          className="w-10 h-10 rounded-full bg-zinc-100 dark:bg-zinc-900 flex items-center justify-center text-zinc-500 dark:text-zinc-400 hover:text-black dark:hover:text-white transition-colors"
        >
          <ArrowLeft size={20} />
        </button>
        <h1 className="text-2xl font-black">Settings</h1>
      </div>

      <div className="space-y-6">
        {/* Preferences */}
        <section>
          <h2 className="text-sm font-bold text-zinc-500 uppercase tracking-widest mb-4 px-2">Preferences</h2>
          <GlassCard className="space-y-1">
            <SettingItem 
              icon={Bell} 
              label="Notifications" 
              value={notifications} 
              onClick={() => setNotifications(!notifications)} 
            />
            <SettingItem 
              icon={Volume2} 
              label="Sound Effects" 
              value={sound} 
              onClick={() => setSound(!sound)} 
            />
            <SettingItem 
              icon={Moon} 
              label="Dark Mode" 
              value={darkMode} 
              onClick={() => updateSettings({ theme: darkMode ? 'light' : 'dark' })} 
            />
          </GlassCard>
        </section>

        {/* Account */}
        <section>
          <h2 className="text-sm font-bold text-zinc-500 uppercase tracking-widest mb-4 px-2">Account</h2>
          <GlassCard className="space-y-1">
            <SettingItem 
              icon={Lock} 
              label="Change Password" 
              type="link" 
              onClick={() => navigate('/change-password')}
            />
          </GlassCard>
        </section>

        {/* Logout */}
        <button 
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 p-4 rounded-2xl bg-red-500/10 text-red-500 font-bold hover:bg-red-500/20 transition-colors border border-red-500/20"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
        
        <div className="text-center text-xs text-zinc-600 font-mono mt-8">
          Version 1.0.0
        </div>
      </div>
    </div>
  );
};

export default Settings;
