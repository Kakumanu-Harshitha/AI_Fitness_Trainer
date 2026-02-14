import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Trophy, Share2, Home, RotateCcw, TrendingUp, ChevronRight } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import ProgressRing from '../components/ProgressRing';
import GradientButton from '../components/GradientButton';

const WorkoutSummary = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { workoutData = {} } = location.state || {};

    const {
        exercise = 'Squat',
        reps = 0,
        duration = 0,
        calories = 0,
        avgScore = 0,
        xpGained = 15,
        currentXP = 450,
        nextLevelXP = 500,
        level = 5,
        badges = [],
    } = workoutData;

    const levelProgress = ((currentXP % nextLevelXP) / nextLevelXP) * 100;

    const handleShare = async () => {
        try {
            if (navigator.share) {
                await navigator.share({
                    title: 'My Workout Result',
                    text: `Just completed ${reps} ${exercise}s with ${avgScore}% form accuracy! 💪 #FitAI`,
                    url: window.location.origin
                });
            } else {
                alert(`Just completed ${reps} ${exercise}s with ${avgScore}% form accuracy! 💪 #FitAI`);
            }
        } catch (error) {
            console.error('Share error:', error);
        }
    };

    return (
        <div className="min-h-screen bg-zinc-950 text-white p-6 pb-24 overflow-y-auto">
            <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                {/* Header */}
                <div className="flex flex-col items-center text-center space-y-4 pt-12">
                    <div className="w-24 h-24 rounded-full bg-primary/20 flex items-center justify-center text-primary animate-bounce">
                        <Trophy size={48} />
                    </div>
                    <div className="space-y-1">
                        <h1 className="text-3xl font-black tracking-tighter uppercase">Workout Complete!</h1>
                        <p className="text-zinc-400 font-bold uppercase text-xs tracking-widest">Great job crushing that session 🔥</p>
                    </div>
                </div>

                {/* Level Progress */}
                <GlassCard className="p-6" neonBorder neonColor="#B4FF39">
                    <div className="flex justify-between items-center mb-4">
                        <span className="text-lg font-black tracking-widest uppercase">Level {level}</span>
                        <span className="text-xl font-black text-primary">+{xpGained} XP</span>
                    </div>
                    <div className="space-y-3">
                        <div className="h-3 bg-zinc-900 rounded-full overflow-hidden border border-white/5">
                            <div 
                                className="h-full bg-primary transition-all duration-1000 ease-out shadow-[0_0_15px_rgba(180,255,57,0.5)]"
                                style={{ width: `${levelProgress}%` }}
                            />
                        </div>
                        <p className="text-center text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                            {currentXP} / {nextLevelXP} XP
                        </p>
                    </div>
                </GlassCard>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-4">
                    <GlassCard className="flex flex-col items-center justify-center p-6 text-center space-y-1">
                        <span className="text-3xl font-black">{reps}</span>
                        <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Reps</span>
                    </GlassCard>

                    <GlassCard className="flex flex-col items-center justify-center p-6 text-center space-y-1">
                        <span className="text-3xl font-black">
                            {Math.floor(duration / 60)}:{(duration % 60).toString().padStart(2, '0')}
                        </span>
                        <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Time</span>
                    </GlassCard>

                    <GlassCard className="flex flex-col items-center justify-center p-6 text-center space-y-1">
                        <span className="text-3xl font-black">{calories}</span>
                        <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Kcal</span>
                    </GlassCard>

                    <GlassCard className="flex flex-col items-center justify-center p-6 text-center space-y-1">
                        <div className="mb-2">
                            <ProgressRing
                                progress={avgScore}
                                size={64}
                                strokeWidth={6}
                                color="#B4FF39"
                            >
                                <span className="text-sm font-black">{avgScore}%</span>
                            </ProgressRing>
                        </div>
                        <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Avg Form</span>
                    </GlassCard>
                </div>

                {/* Badges */}
                {badges && badges.length > 0 && (
                    <GlassCard className="p-6 space-y-4">
                        <h3 className="text-sm font-black uppercase tracking-widest flex items-center gap-2">
                            <Trophy size={16} className="text-primary" />
                            Achievements Unlocked
                        </h3>
                        <div className="flex flex-wrap gap-3">
                            {badges.map((badge, index) => (
                                <div key={index} className="bg-primary/10 border border-primary/20 rounded-2xl p-4 flex flex-col items-center min-w-[100px] space-y-2">
                                    <span className="text-3xl">{badge.emoji}</span>
                                    <span className="text-[10px] font-black uppercase text-center leading-tight">{badge.name}</span>
                                </div>
                            ))}
                        </div>
                    </GlassCard>
                )}

                {/* Actions */}
                <div className="flex gap-4">
                    <button 
                        onClick={handleShare}
                        className="flex-1 h-14 bg-zinc-900 border border-white/10 rounded-2xl flex items-center justify-center gap-3 text-zinc-400 font-bold uppercase tracking-widest hover:text-white hover:bg-zinc-800 transition-all active:scale-95"
                    >
                        <Share2 size={20} />
                        Share
                    </button>

                    <GradientButton
                        title="Back to Home"
                        onPress={() => navigate('/dashboard')}
                        className="flex-[2] h-14"
                    />
                </div>

                {/* Quick Stats */}
                <GlassCard className="p-6 space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center text-green-500">
                            <TrendingUp size={18} />
                        </div>
                        <p className="text-sm font-bold text-zinc-300">
                            Personal best: <span className="text-white font-black">{reps} reps</span>
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500">
                            <Trophy size={18} />
                        </div>
                        <p className="text-sm font-bold text-zinc-300">
                            Streak: <span className="text-white font-black">7 days 🔥</span>
                        </p>
                    </div>
                </GlassCard>
            </div>
        </div>
    );
};

export default WorkoutSummary;
