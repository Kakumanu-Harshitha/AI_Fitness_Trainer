import React, { useState, useEffect } from 'react';
import {
  User,
  Trophy,
  Target,
  Flame,
  Settings as SettingsIcon,
  LogOut,
  Edit,
  Award,
  Zap
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import GlassCard from '../components/GlassCard';
import { useApp } from '../contexts/AppContext';
import { useApi } from '../hooks/useApi';

const Profile = () => {
  const navigate = useNavigate();
  const { logout } = useApp();
  const { get } = useApi();
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const data = await get('/profile');
      if (data) {
        const transformedData = {
          username: data.username,
          email: data.email || 'user@fitai.com',
          level: Math.floor((data.points / 100) ** 0.5) + 1,
          xp: data.points,
          nextLevelXP: (Math.floor((data.points / 100) ** 0.5) + 1) ** 2 * 100,
          totalWorkouts: data.total_workouts || 0,
          streak: data.streak || 0,
          badges: [
            { id: 1, name: 'First Workout', emoji: '🎯', unlocked: true },
            { id: 2, name: '7 Day Streak', emoji: '🔥', unlocked: (data.streak || 0) >= 7 },
            { id: 3, name: 'Perfect Form', emoji: '💎', unlocked: true },
            { id: 4, name: '100 Workouts', emoji: '💯', unlocked: false },
            { id: 5, name: 'Early Bird', emoji: '🌅', unlocked: true },
            { id: 6, name: 'Night Owl', emoji: '🦉', unlocked: false },
          ],
          stats: {
            totalReps: data.total_reps || 0,
            avgScore: data.avg_score || 0,
            caloriesBurned: data.total_calories || 0,
            minutesActive: Math.floor((data.total_duration || 0) / 60)
          }
        };
        setUserData(transformedData);
      } else {
        setUserData(getMockUserData());
      }
    } catch (error) {
      console.error('Fetch user data failed:', error);
      setUserData(getMockUserData());
    }
  };

  const getMockUserData = () => ({
    username: 'FitWarrior',
    email: 'user@fitai.com',
    level: 12,
    xp: 2450,
    nextLevelXP: 3000,
    totalWorkouts: 87,
    streak: 15,
    badges: [
      { id: 1, name: 'First Workout', emoji: '🎯', unlocked: true },
      { id: 2, name: '7 Day Streak', emoji: '🔥', unlocked: true },
      { id: 3, name: 'Perfect Form', emoji: '💎', unlocked: true },
      { id: 4, name: '100 Workouts', emoji: '💯', unlocked: false },
      { id: 5, name: 'Early Bird', emoji: '🌅', unlocked: true },
      { id: 6, name: 'Night Owl', emoji: '🦉', unlocked: false },
    ],
    stats: {
      totalReps: 5420,
      avgScore: 88,
      caloriesBurned: 12450,
      minutesActive: 1850
    }
  });

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      await logout();
      navigate('/login');
    }
  };

  const data = userData || getMockUserData();
  const levelProgress = ((data.xp % data.nextLevelXP) / data.nextLevelXP) * 100;

  return (
    <div className="min-h-screen bg-black text-white p-6 pb-24 max-w-2xl mx-auto overflow-y-auto">
      {/* Profile Header */}
      <GlassCard className="p-6 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="flex items-center gap-6 mb-8">
          <div className="relative">
            <div className="w-20 h-20 rounded-3xl bg-primary/15 border-2 border-primary flex items-center justify-center">
              <User size={40} className="text-primary" />
            </div>
            <button 
              onClick={() => navigate('/edit-profile')}
              className="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-primary flex items-center justify-center text-black shadow-lg hover:scale-110 transition-transform"
            >
              <Edit size={14} />
            </button>
          </div>
          <div>
            <h1 className="text-2xl font-black">{data.username}</h1>
            <p className="text-zinc-500">{data.email}</p>
          </div>
        </div>

        {/* Level Progress */}
        <div className="space-y-3">
          <div className="flex justify-between items-center font-black">
            <span className="text-primary tracking-widest text-sm">LEVEL {data.level}</span>
            <span className="text-zinc-500 text-xs">{data.xp} / {data.nextLevelXP} XP</span>
          </div>
          <div className="h-2 bg-zinc-900 rounded-full overflow-hidden">
            <div 
              className="h-full bg-primary transition-all duration-1000" 
              style={{ width: `${levelProgress}%` }} 
            />
          </div>
        </div>
      </GlassCard>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        {[
          { label: 'Workouts', value: data.totalWorkouts, icon: Zap, color: 'text-primary' },
          { label: 'Day Streak', value: data.streak, icon: Flame, color: 'text-orange-500' },
          { label: 'Avg Score', value: `${data.stats?.avgScore || 0}%`, icon: Trophy, color: 'text-yellow-500' },
          { label: 'Total Reps', value: data.stats?.totalReps || 0, icon: Target, color: 'text-blue-500' }
        ].map((stat, index) => (
          <GlassCard key={index} className="p-6 flex flex-col items-center gap-2 animate-in fade-in slide-in-from-bottom-4 duration-500" style={{ animationDelay: `${(index + 2) * 100}ms` }}>
            <stat.icon size={20} className={stat.color} />
            <p className="text-2xl font-black">{stat.value}</p>
            <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">{stat.label}</p>
          </GlassCard>
        ))}
      </div>

      {/* Badges Showcase */}
      <GlassCard className="p-6 mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-500">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Award size={24} className="text-yellow-500" />
            <h2 className="text-lg font-black">Achievements</h2>
          </div>
          <span className="text-primary font-bold">
            {data.badges.filter(b => b.unlocked).length}/{data.badges.length}
          </span>
        </div>
        <div className="grid grid-cols-3 gap-3">
          {data.badges.map((badge) => (
            <div
              key={badge.id}
              className={`aspect-square rounded-2xl flex flex-col items-center justify-center p-3 border transition-all ${
                badge.unlocked 
                  ? 'bg-primary/10 border-primary/20' 
                  : 'bg-zinc-900/30 border-zinc-900 opacity-40'
              }`}
            >
              <span className={`text-3xl mb-2 ${badge.unlocked ? '' : 'grayscale'}`}>
                {badge.emoji}
              </span>
              <span className="text-[10px] font-bold text-center leading-tight">
                {badge.name}
              </span>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* Settings & Logout */}
      <div className="space-y-3 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-700">
        <button 
          onClick={() => navigate('/onboarding')}
          className="w-full flex items-center gap-4 p-4 rounded-2xl bg-zinc-900/50 text-zinc-400 font-bold hover:bg-zinc-900 transition-colors"
        >
          <SettingsIcon size={20} />
          <span>Settings</span>
        </button>

        <button 
          onClick={handleLogout}
          className="w-full flex items-center gap-4 p-4 rounded-2xl bg-red-500/10 text-red-500 font-bold hover:bg-red-500/20 transition-colors"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Profile;
