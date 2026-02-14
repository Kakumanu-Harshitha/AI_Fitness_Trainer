import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Flame, 
  Clock, 
  Dumbbell, 
  Zap, 
  Play, 
  Wifi, 
  WifiOff, 
  Trophy, 
  TrendingUp, 
  Target, 
  X, 
  Star, 
  Heart, 
  ShieldAlert, 
  Plus,
  RefreshCw
} from 'lucide-react';
import GlassCard from '../components/GlassCard';
import WaterTrackerCard from '../components/WaterTrackerCard';
import GradientButton from '../components/GradientButton';
import ProgressRing from '../components/ProgressRing';
import { useApi } from '../hooks/useApi';
import { useApp } from '../contexts/AppContext';

const HomeDashboard = () => {
  const navigate = useNavigate();
  const { get, post } = useApi();
  const { user } = useApp();
  const [dashboardData, setDashboardData] = useState(null);
  const [routines, setRoutines] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [showCoachModal, setShowCoachModal] = useState(false);
  const [selectedRoutine, setSelectedRoutine] = useState(null);
  const [isPremium, setIsPremium] = useState(true);
  const [displayProgress, setDisplayProgress] = useState(0);

  const personas = [
    {
      id: 'supportive',
      name: 'Supportive Coach',
      description: 'Kind, encouraging, and perfect for beginners.',
      icon: <Heart size={24} className="text-pink-500" />,
      premium: false,
      color: '#ec4899'
    },
    {
      id: 'drill_sergeant',
      name: 'Drill Sergeant',
      description: 'High intensity, no excuses, and aggressive motivation.',
      icon: <ShieldAlert size={24} className="text-red-500" />,
      premium: true,
      color: '#ef4444'
    },
    {
      id: 'tech_expert',
      name: 'Tech Expert',
      description: 'Data-driven, focused on form and joint angles.',
      icon: <Star size={24} className="text-primary" />,
      premium: true,
      color: '#B4FF39'
    }
  ];

  const fetchDashboardData = async () => {
    try {
      const data = await get('/dashboard/home');
      if (data) {
        setDashboardData(data);
        const cal = data.stats_summary.calories || 0;
        const goal = data.stats_summary.calories_goal || 500;
        setDisplayProgress(Math.round(Math.min(cal / goal, 1) * 100));
      }
    } catch (e) {
      console.error("Fetch dashboard data failed:", e);
    }
  };

  const fetchRoutines = async () => {
    try {
      const data = await get('/routines/');
      if (data) {
        setRoutines(data);
      }
    } catch (e) {
      console.error("Fetch routines failed:", e);
    }
  };

  const handleLogWater = async (amount) => {
    try {
      await post('/water/log', { amount_ml: amount });
      fetchDashboardData();
    } catch (error) {
      console.error("Failed to log water:", error);
    }
  };

  const handleRemoveWater = async (amount) => {
    try {
      if ((dashboardData?.water_intake?.current || 0) <= 0) return;
      await post('/water/log', { amount_ml: -amount });
      fetchDashboardData();
    } catch (error) {
      console.error("Failed to remove water:", error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([fetchDashboardData(), fetchRoutines()]);
    setRefreshing(false);
  };

  const handleStartWorkout = (personaId) => {
    setShowCoachModal(false);
    const routineToStart = selectedRoutine || dashboardData?.ai_pulse || { id: 'custom', name: 'Live Session' };
    navigate('/live-workout', { 
      state: { 
        routine: routineToStart,
        persona: personaId 
      }
    });
  };

  useEffect(() => {
    fetchDashboardData();
    fetchRoutines();
    // WebSocket logic would go here, simplified for now
    setWsConnected(true);
  }, []);

  const weeklyProgress = dashboardData?.weekly_progress || [false, false, false, false, false, false, false];

  return (
    <div className="min-h-screen bg-black text-white p-6 pb-24 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-start mb-8 animate-in fade-in slide-in-from-top-4 duration-500">
        <div>
          <h1 className="text-2xl font-black">{dashboardData?.greeting || `Hi, ${user?.username || 'User'}!`} 👋</h1>
          <p className="text-zinc-500 text-sm">Ready to crush your goals?</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-2 px-4 flex items-center gap-3">
            <div className="text-right">
              <p className="text-xl font-black text-orange-500 leading-none">{dashboardData?.streak || 0}</p>
              <p className="text-[8px] font-bold text-zinc-500 uppercase tracking-tighter">DAY STREAK</p>
            </div>
            <Flame size={28} className="text-orange-500 fill-orange-500" />
          </div>
          <div className={`p-1 px-2 rounded-full text-[10px] font-bold flex items-center gap-1 ${wsConnected ? 'text-green-500 bg-green-500/10' : 'text-red-500 bg-red-500/10'}`}>
            {wsConnected ? <Wifi size={12} /> : <WifiOff size={12} />}
            {wsConnected ? 'LIVE' : 'OFFLINE'}
          </div>
        </div>
      </div>

      {/* Weekly Progress */}
      <div className="mb-8 animate-in fade-in slide-in-from-top-4 duration-500 delay-100">
        <p className="text-[10px] font-extrabold text-zinc-500 uppercase tracking-widest mb-3">Last 7 Days</p>
        <div className="flex justify-between gap-2">
          {weeklyProgress.map((completed, index) => (
            <div
              key={index}
              className={`h-2 flex-1 rounded-full transition-all duration-500 ${completed ? 'bg-primary' : 'bg-zinc-800'}`}
            />
          ))}
        </div>
      </div>

      {/* AI Pulse Card */}
      {dashboardData?.ai_pulse && (
        <GlassCard className="mb-8 border-primary/30 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-200" neonBorder neonColor="#B4FF39">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
              <Zap size={20} className="text-primary" />
            </div>
            <div className="flex-1">
              <p className="text-[10px] font-extrabold text-primary uppercase tracking-widest">AI PULSE</p>
              <h2 className="text-xl font-black">{dashboardData.ai_pulse.title}</h2>
            </div>
            <button 
              onClick={() => {
                setSelectedRoutine(dashboardData.ai_pulse);
                setShowCoachModal(true);
              }}
              className="w-10 h-10 rounded-full bg-primary flex items-center justify-center hover:scale-110 transition-transform active:scale-95"
            >
              <Play size={18} className="text-black fill-black ml-0.5" />
            </button>
          </div>
          <div className="flex gap-4">
            <div className="flex items-center gap-1.5 text-xs text-zinc-400">
              <Clock size={14} />
              <span>{dashboardData.ai_pulse.duration} min</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-zinc-400">
              <Flame size={14} />
              <span>{dashboardData.ai_pulse.calories} kcal</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-zinc-400">
              <Dumbbell size={14} />
              <span>{dashboardData.ai_pulse.exercises.length} exercises</span>
            </div>
          </div>
        </GlassCard>
      )}

      {/* Water Tracker */}
      <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 delay-300">
        <WaterTrackerCard 
          current={dashboardData?.water_intake?.current || 0}
          goal={dashboardData?.water_intake?.goal || 2500}
          onAdd={handleLogWater}
          onRemove={handleRemoveWater}
        />
      </div>

      {/* Daily Summary */}
      <GlassCard className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-400">
        <div className="flex justify-between items-center mb-6">
          <div>
            <p className="text-[10px] font-extrabold text-zinc-500 uppercase tracking-widest">TODAY'S ACTIVITY</p>
            <h2 className="text-xl font-black">Daily Summary</h2>
          </div>
          <ProgressRing
            progress={displayProgress}
            size={64}
            strokeWidth={6}
            color="#22c55e"
          >
            <span className="text-xs font-black text-white">{displayProgress}%</span>
          </ProgressRing>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="flex flex-col items-center p-3 bg-zinc-900/50 rounded-2xl border border-zinc-800">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center mb-2">
              <Clock size={16} className="text-cyan-400" />
            </div>
            <p className="text-lg font-black">{dashboardData?.stats_summary?.minutes || 0}</p>
            <p className="text-[8px] font-bold text-zinc-500 uppercase">MIN</p>
          </div>
          <div className="flex flex-col items-center p-3 bg-zinc-900/50 rounded-2xl border border-zinc-800">
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center mb-2">
              <Dumbbell size={16} className="text-purple-400" />
            </div>
            <p className="text-lg font-black">{dashboardData?.stats_summary?.exercises || 0}</p>
            <p className="text-[8px] font-bold text-zinc-500 uppercase">EXS</p>
          </div>
          <div className="flex flex-col items-center p-3 bg-zinc-900/50 rounded-2xl border border-zinc-800">
            <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center mb-2">
              <Zap size={16} className="text-orange-400" />
            </div>
            <p className="text-lg font-black">{dashboardData?.stats_summary?.calories || 0}</p>
            <p className="text-[8px] font-bold text-zinc-500 uppercase">KCAL</p>
          </div>
        </div>

        <button 
          onClick={() => setShowCoachModal(true)}
          className="w-full bg-white text-black font-black py-4 rounded-2xl flex items-center justify-center gap-2 hover:bg-zinc-200 transition-colors active:scale-[0.98]"
        >
          <Play size={20} className="fill-black" />
          Quick Start
        </button>
      </GlassCard>

      {/* My Routines */}
      {routines.length > 0 && (
        <div className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-500">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xs font-black text-zinc-500 uppercase tracking-widest">MY ROUTINES</h2>
            <button onClick={() => navigate('/workouts')} className="text-primary text-xs font-bold flex items-center gap-1">
              See All <Plus size={14} />
            </button>
          </div>
          <div className="flex gap-4 overflow-x-auto pb-4 no-scrollbar">
            {routines.map((routine, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setSelectedRoutine(routine);
                  setShowCoachModal(true);
                }}
                className="flex-shrink-0 w-40 p-4 bg-zinc-900/50 border border-zinc-800 rounded-2xl text-left hover:border-zinc-700 transition-all active:scale-95"
              >
                <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center mb-3">
                  <Dumbbell size={16} className="text-blue-400" />
                </div>
                <h3 className="font-bold text-sm mb-1 truncate">{routine.name}</h3>
                <p className="text-[10px] text-zinc-500">{routine.steps?.length || 0} exercises</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Grid Stats */}
      <div className="grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-600">
        <div className="p-4 bg-zinc-900/30 border border-orange-500/10 rounded-2xl">
          <div className="flex justify-between items-center mb-3">
            <Flame size={20} className="text-orange-500" />
            <span className="text-[8px] font-black text-zinc-500">GOAL: {dashboardData?.stats_summary?.calories_goal || 500}</span>
          </div>
          <p className="text-2xl font-black mb-1">{dashboardData?.stats_summary?.calories || 0}</p>
          <p className="text-[10px] font-bold text-zinc-500 uppercase">Calories Today</p>
        </div>
        <div className="p-4 bg-zinc-900/30 border border-green-500/10 rounded-2xl">
          <div className="flex justify-between items-center mb-3">
            <Zap size={20} className="text-green-500" />
            <span className="text-[8px] font-black text-green-500">
              {dashboardData?.stats_summary?.posture_trend >= 0 ? '+' : ''}{dashboardData?.stats_summary?.posture_trend || 0}% THIS WEEK
            </span>
          </div>
          <p className="text-2xl font-black mb-1">{dashboardData?.stats_summary?.avg_posture_score || 0}%</p>
          <p className="text-[10px] font-bold text-zinc-500 uppercase">Posture Score</p>
        </div>
      </div>

      {/* Refresh Button (Float) */}
      <button 
        onClick={onRefresh}
        className={`fixed bottom-24 right-6 w-12 h-12 bg-zinc-900 border border-zinc-800 rounded-full flex items-center justify-center shadow-2xl transition-all active:rotate-180 ${refreshing ? 'animate-spin' : ''}`}
      >
        <RefreshCw size={20} className="text-primary" />
      </button>

      {/* Coach Modal */}
      {showCoachModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-4 animate-in fade-in duration-300">
          <div className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-t-[32px] sm:rounded-[32px] p-6 animate-in slide-in-from-bottom-8 duration-300">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-black">Choose Your Coach</h2>
                <p className="text-zinc-500 text-sm">Premium AI coaching experience</p>
              </div>
              <button onClick={() => setShowCoachModal(false)} className="p-2 bg-zinc-800 rounded-full text-zinc-500">
                <X size={24} />
              </button>
            </div>

            <div className="space-y-4 mb-8">
              {personas.map((p) => (
                <button
                  key={p.id}
                  disabled={p.premium && !isPremium}
                  onClick={() => handleStartWorkout(p.id)}
                  className={`w-full flex items-center gap-4 p-4 rounded-2xl border transition-all text-left active:scale-[0.98] ${p.premium && !isPremium ? 'opacity-50 border-zinc-800 bg-zinc-950/50 cursor-not-allowed' : 'bg-zinc-900 border-zinc-800 hover:border-zinc-700'}`}
                >
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${p.color}15` }}>
                    {p.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="font-bold">{p.name}</span>
                      {p.premium && (
                        <div className="flex items-center gap-0.5 px-1.5 py-0.5 bg-primary rounded text-[8px] font-black text-black">
                          <Zap size={8} className="fill-black" /> PREMIUM
                        </div>
                      )}
                    </div>
                    <p className="text-xs text-zinc-500">{p.description}</p>
                  </div>
                  <Play size={20} style={{ color: p.color, fill: p.color }} />
                </button>
              ))}
            </div>

            {!isPremium && (
              <div className="bg-primary/5 border border-primary/20 rounded-2xl p-4 mb-4">
                <h3 className="font-bold text-sm mb-1">Unlock All Coaches</h3>
                <p className="text-[10px] text-zinc-500 mb-4">Get the full Drill Sergeant and Zen experience with Pro.</p>
                <button className="w-full bg-primary text-black font-black py-3 rounded-xl text-sm">Upgrade Now</button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default HomeDashboard;
