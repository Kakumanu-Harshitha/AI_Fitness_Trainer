import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Award, 
  Target, 
  Flame, 
  Zap,
  Activity
} from 'lucide-react';
import GlassCard from '../components/GlassCard';
import { useApi } from '../hooks/useApi';

const Stats = () => {
  const { get } = useApi();
  const [timeRange, setTimeRange] = useState('week'); // 'week', 'month', 'year'
  const [statsData, setStatsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, [timeRange]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await get(`/stats?range=${timeRange}`);
      if (data) {
        setStatsData(data);
      }
    } catch (error) {
      console.error('Fetch stats failed:', error);
      setStatsData(getMockStats());
    } finally {
      setLoading(false);
    }
  };

  const getMockStats = () => ({
    totalWorkouts: 42,
    totalMinutes: 1260,
    avgScore: 87,
    caloriesBurned: 8400,
    fatigueData: [85, 88, 82, 90, 87, 84, 89],
    jointStress: [45, 32, 28, 38, 25],
    weeklyWorkouts: [3, 5, 4, 6, 5, 4, 7],
    personalBests: [
      { exercise: 'Squats', reps: 50, date: '2026-01-28' },
      { exercise: 'Push-ups', reps: 35, date: '2026-01-25' }
    ]
  });

  const data = statsData || getMockStats();

  return (
    <div className="min-h-screen bg-black text-white p-6 pb-24 max-w-2xl mx-auto overflow-y-auto">
      {/* Header */}
      <div className="mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <h1 className="text-3xl font-black mb-6">Your Stats</h1>
        <div className="flex gap-2">
          {['week', 'month', 'year'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                timeRange === range 
                  ? 'bg-primary text-black scale-105' 
                  : 'bg-zinc-900/50 text-zinc-500 hover:bg-zinc-900'
              }`}
            >
              {range.charAt(0).toUpperCase() + range.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Overview Grid */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        {[
          { label: 'Workouts', value: data.totalWorkouts, icon: Zap, color: 'text-primary', bg: 'bg-primary/10' },
          { label: 'Avg Score', value: `${data.avgScore}%`, icon: TrendingUp, color: 'text-blue-500', bg: 'bg-blue-500/10' },
          { label: 'Calories', value: data.caloriesBurned, icon: Flame, color: 'text-orange-500', bg: 'bg-orange-500/10' },
          { label: 'Minutes', value: data.totalMinutes, icon: Target, color: 'text-green-500', bg: 'bg-green-500/10' }
        ].map((stat, index) => (
          <GlassCard key={index} className="flex flex-col items-center p-6 animate-in fade-in slide-in-from-bottom-4 duration-500" style={{ animationDelay: `${(index + 2) * 100}ms` }}>
            <div className={`w-10 h-10 rounded-xl ${stat.bg} flex items-center justify-center ${stat.color} mb-3`}>
              <stat.icon size={20} />
            </div>
            <p className="text-2xl font-black">{stat.value}</p>
            <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">{stat.label}</p>
          </GlassCard>
        ))}
      </div>

      {/* Simple Visualizations for Web */}
      <div className="space-y-6">
        {/* Weekly Activity */}
        <GlassCard className="p-6 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-500">
          <h2 className="text-lg font-black mb-6">Weekly Activity</h2>
          <div className="flex items-end justify-between h-32 gap-2">
            {data.weeklyWorkouts.map((count, index) => (
              <div key={index} className="flex-1 flex flex-col items-center gap-2">
                <div 
                  className="w-full bg-primary rounded-t-lg transition-all duration-1000"
                  style={{ height: `${(count / 7) * 100}%`, minHeight: '4px' }}
                />
                <span className="text-[10px] font-bold text-zinc-500">{['M', 'T', 'W', 'T', 'F', 'S', 'S'][index]}</span>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Personal Bests */}
        <GlassCard className="p-6 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-700">
          <div className="flex items-center gap-3 mb-6">
            <Award size={24} className="text-yellow-500" />
            <h2 className="text-lg font-black">Personal Bests</h2>
          </div>
          <div className="space-y-4">
            {data.personalBests.map((best, index) => (
              <div key={index} className="flex items-center justify-between py-3 border-b border-zinc-900 last:border-0">
                <div>
                  <p className="font-bold">{best.exercise}</p>
                  <p className="text-xs text-zinc-500">{best.date}</p>
                </div>
                <p className="text-xl font-black text-primary">{best.reps} reps</p>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Fatigue Analysis (Simple Bar) */}
        <GlassCard className="p-6 animate-in fade-in slide-in-from-bottom-4 duration-500 delay-1000">
          <div className="flex items-center gap-3 mb-6">
            <Activity size={24} className="text-red-500" />
            <h2 className="text-lg font-black">Performance Health</h2>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-bold mb-2">
                <span className="text-zinc-500 uppercase">Recovery Rate</span>
                <span className="text-primary">85%</span>
              </div>
              <div className="h-2 bg-zinc-900 rounded-full overflow-hidden">
                <div className="h-full bg-primary w-[85%] rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs font-bold mb-2">
                <span className="text-zinc-500 uppercase">Joint Stress</span>
                <span className="text-orange-500">Low</span>
              </div>
              <div className="h-2 bg-zinc-900 rounded-full overflow-hidden">
                <div className="h-full bg-orange-500 w-[30%] rounded-full" />
              </div>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

export default Stats;
