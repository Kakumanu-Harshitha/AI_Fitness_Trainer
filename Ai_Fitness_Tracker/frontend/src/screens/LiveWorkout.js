import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
    X, Play, Pause, RotateCcw, ChevronRight, 
    Activity, Clock, Zap, Volume2, VolumeX, 
    Mic, Send, Loader2, Trophy, Frown
} from 'lucide-react';
import { useApp } from '../contexts/AppContext';
import { useWorkout } from '../contexts/WorkoutContext';
import CameraView from '../components/CameraView';
import GlassCard from '../components/GlassCard';
import VoiceModal from '../components/VoiceModal';
import { API_URL } from '../utils/api';

const LiveWorkout = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { routine, persona, duelMode, opponent } = location.state || {};
    const { token, settings, sendDuelProgress } = useApp();
    const {
        isActive,
        currentExercise,
        sessionStats,
        phase,
        startWorkout,
        updateWorkoutStats,
        incrementTime,
        pauseWorkout,
        resumeWorkout,
        completeWorkout,
        resetWorkout,
    } = useWorkout();

    const [isMuted, setIsMuted] = useState(false);
    const [isAudioEnabled, setIsAudioEnabled] = useState(false);
    const [advice, setAdvice] = useState('Welcome! Adjust your camera to start.');
    const [lastSpokenAdvice, setLastSpokenAdvice] = useState('');
    const [isVoiceModalVisible, setIsVoiceModalVisible] = useState(false);
    const [isCounting, setIsCounting] = useState(false);
    const cameraRef = useRef(null);
    const timerRef = useRef(null);
    const lastAdviceTime = useRef(0);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    useEffect(() => {
        if (!isActive) {
            const initialExercise = routine?.exercises?.[0] || 'squats';
            startWorkout(
                routine || { id: 'custom', name: 'Live Session' },
                initialExercise
            );
        }

        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
        };
    }, []);

    // Start counting once camera is ready
    useEffect(() => {
        if (isActive && !isCounting) {
            const timer = setTimeout(() => {
                resumeWorkout(); // This sets phase to 'workout'
                setIsCounting(true);
            }, 3000); // 3 second delay for camera setup
            return () => clearTimeout(timer);
        }
    }, [isActive, isCounting]);

    // Speech handler
    const speakAdvice = (text, force = false) => {
        const isVoiceEnabled = settings?.voiceCoachEnabled !== false;
        
        if (isMuted || !isVoiceEnabled || !text || phase === 'rest') {
            return;
        }

        const now = Date.now();
        const isSameAdvice = text === lastSpokenAdvice;
        const cooldown = isSameAdvice ? 5000 : 2000;

        if (force || (now - lastAdviceTime.current > cooldown)) {
            lastAdviceTime.current = now;
            setLastSpokenAdvice(text);

            if ('speechSynthesis' in window) {
                // If force is true, cancel current speech (for user questions)
                if (force) {
                    window.speechSynthesis.cancel();
                }

                if (!window.speechSynthesis.speaking || force) {
                    const utterance = new SpeechSynthesisUtterance(text);
                    const activePersona = persona || 'supportive';
                    
                    // Simplified voice config for web
                    utterance.rate = activePersona === 'drill_sergeant' ? 1.1 : 1.0;
                    utterance.pitch = activePersona === 'zen_coach' ? 0.9 : 1.0;
                    utterance.volume = 1.0;
                    
                    window.speechSynthesis.speak(utterance);
                }
            }
        }
    };

    useEffect(() => {
        if (advice && advice !== 'Starting your session...') {
            speakAdvice(advice);
        }
    }, [advice]);

    useEffect(() => {
        if (phase === 'workout' && !timerRef.current) {
            // Initial greeting when workout starts
            if (!isAudioEnabled) {
                const greetings = {
                    supportive: "Hello! I'm your supportive coach. Let's have a great workout together!",
                    drill_sergeant: "ATTENTION! I'M YOUR DRILL SERGEANT. NO SLACKING OFF! MOVE!",
                    zen_coach: "Welcome. Let us find focus and harmony in our movement today."
                };
                const selectedPersona = persona || 'supportive';
                setAdvice(greetings[selectedPersona] || greetings.supportive);
                setIsAudioEnabled(true);
            }

            timerRef.current = setInterval(() => {
                incrementTime();
            }, 1000);
        } else if (phase !== 'workout' && timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
        }
    }, [phase]);

    const handleVoiceSubmit = async (question) => {
        if (!token) {
            throw new Error('Please log in to use the AI Coach');
        }

        try {
            const sanitizedContext = {
                reps: Number(sessionStats.reps) || 0,
                avg_score: Number(sessionStats.avgScore) || 0,
                calories: Number(sessionStats.calories) || 0,
                time: Number(sessionStats.time) || 0,
                exercise: String(currentExercise || 'unknown'),
            };

            const response = await fetch(`${API_URL}/voice/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    command: question,
                    persona: persona || 'supportive',
                    session_context: sanitizedContext
                }),
            });

            const data = await response.json();
            if (response.ok && data.status === 'success') {
                speakAdvice(data.response, true); // Force speak user question response
                return data.response;
            }
            throw new Error(data.detail || data.message || 'Failed to process voice command');
        } catch (error) {
            console.error('[LiveWorkout] Voice command error:', error);
            throw error;
        }
    };

    const handleComplete = async () => {
        // Get the latest stats before completing
        const finalStats = completeWorkout();
        console.log('[LiveWorkout] Final stats for summary:', finalStats);
        
        try {
            if (!token) {
                console.warn('[LiveWorkout] No token found, skipping save');
            } else {
                const response = await fetch(`${API_URL}/workouts/save`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        exercise: typeof currentExercise === 'string' ? currentExercise : (currentExercise?.name || 'Squat'),
                        reps: Number(finalStats.reps),
                        duration: Number(finalStats.time),
                        calories: Number(finalStats.calories),
                        posture_score: Number(finalStats.avgScore),
                        avg_angle: 0.0
                    })
                });
                
                if (response.ok) {
                    console.log('[LiveWorkout] Workout saved to backend');
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    console.error('[LiveWorkout] Failed to save workout:', response.status, errorData);
                }
            }
        } catch (error) {
            console.error('[LiveWorkout] Failed to save workout error:', error);
        }

        // Calculate XP based on performance
        let xpGained = Math.floor(finalStats.reps * 0.5 + (finalStats.time / 60) * 2);
        let currentXP = 0;
        let level = 1;

        if (token) {
            try {
                const profileRes = await fetch(`${API_URL}/profile`, { 
                    headers: { 'Authorization': `Bearer ${token}` } 
                });
                if (profileRes.ok) {
                    const profileData = await profileRes.json();
                    currentXP = profileData.xp || 0;
                    level = profileData.level || 1;
                }
            } catch (err) {
                console.error('[LiveWorkout] Failed to fetch profile:', err);
            }
        }

        navigate('/workout-summary', { 
            state: { 
                workoutData: {
                    exercise: currentExercise || 'Squat',
                    reps: finalStats.reps,
                    duration: finalStats.time,
                    calories: Math.round(finalStats.calories),
                    avgScore: finalStats.avgScore,
                    xpGained,
                    currentXP,
                    nextLevelXP: 1000,
                    level,
                    badges: []
                }
            }
        });
    };

    const toggleMute = () => {
        setIsMuted(!isMuted);
        if (!isAudioEnabled) setIsAudioEnabled(true);
    };

    const [isProactiveLoading, setIsProactiveLoading] = useState(false);
    const lastLLMRepCount = useRef(0);
    const [opponentReps, setOpponentReps] = useState(0);
    const [duelResult, setDuelResult] = useState(null); // 'won' | 'lost' | null

    // Duel Mode Listener
    useEffect(() => {
        if (!duelMode) return;

        const handleDuelProgress = (e) => {
            console.log('[LiveWorkout] Opponent progress:', e.detail);
            const { reps } = e.detail;
            setOpponentReps(reps);
            
            if (reps >= 20 && !duelResult) {
                setDuelResult('lost');
                pauseWorkout();
                speakAdvice("Opponent won the duel. Better luck next time!");
            }
        };

        window.addEventListener('duel-progress', handleDuelProgress);
        return () => window.removeEventListener('duel-progress', handleDuelProgress);
    }, [duelMode, opponent, duelResult]);

    // ... (rest of the code)

    const handleLandmarks = async (landmarks) => {
        if (!landmarks || landmarks.length === 0 || duelResult) return;
        
        if (phase === 'workout' && isActive) {
            try {
                const result = updateWorkoutStats(landmarks);
                
                if (result) {
                    // Duel Progress Update
                    if (duelMode && result.reps && result.reps.repCount > 0) {
                        sendDuelProgress(result.reps.repCount, opponent?.username);
                        if (result.reps.repCount >= 20 && !duelResult) {
                            setDuelResult('won');
                            pauseWorkout();
                            speakAdvice("Congratulations! You won the duel!");
                        }
                    }

                    if (result.advice) {
                        setAdvice(result.advice);
                    }

                    // Proactive LLM Advice every 10 reps or on significant events
                    const currentReps = result.reps?.repCount || 0;
                    if (currentReps > 0 && currentReps % 10 === 0 && currentReps !== lastLLMRepCount.current && !isProactiveLoading) {
                        lastLLMRepCount.current = currentReps;
                        getProactiveAdvice(currentReps);
                    }
                }
            } catch (error) {
                console.error('[LiveWorkout] Error updating workout stats:', error);
            }
        }
    };

    const getProactiveAdvice = async (reps) => {
        if (!token || isProactiveLoading) return;
        
        setIsProactiveLoading(true);
        try {
            const context = {
                reps: reps,
                avg_score: sessionStats.avgScore,
                calories: sessionStats.calories,
                time: sessionStats.time,
                exercise: currentExercise || 'squat'
            };

            const response = await fetch(`${API_URL}/voice/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    command: "Give me a quick progress update and a tip.",
                    persona: persona || 'supportive',
                    session_context: context
                }),
            });

            if (response.ok) {
                const data = await response.json();
                if (data.response) {
                    setAdvice(data.response);
                    speakAdvice(data.response, true); // Force speak proactive advice
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                console.error('[LiveWorkout] Proactive advice failed:', response.status, errorData);
            }
        } catch (error) {
            console.error('[LiveWorkout] Proactive advice error:', error);
        } finally {
            setIsProactiveLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black overflow-hidden flex flex-col">
            {/* Camera Background */}
            <div className="absolute inset-0 z-0">
                <CameraView
                    ref={cameraRef}
                    onLandmarks={handleLandmarks}
                />
            </div>

            {/* Header Overlay */}
            <div className="relative z-10 p-6 bg-gradient-to-b from-white/90 dark:from-black/80 to-transparent transition-colors duration-300">
                <div className="flex items-center justify-between">
                    <button 
                        onClick={() => navigate(-1)}
                        className="w-11 h-11 rounded-full bg-gray-100 dark:bg-white/10 backdrop-blur-md flex items-center justify-center text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-white/20 transition-colors"
                    >
                        <X size={24} />
                    </button>

                    {/* Duel Opponent Card */}
                    {duelMode && (
                        <div className="absolute top-20 right-4 w-40 p-4 bg-red-100/80 dark:bg-red-900/80 backdrop-blur-md rounded-xl border border-red-200 dark:border-red-500 animate-in slide-in-from-right duration-500">
                            <p className="text-xs text-red-600 dark:text-red-300 font-bold uppercase tracking-wider">Opponent</p>
                            <p className="text-lg font-black text-gray-900 dark:text-white truncate">{opponent?.username || 'Enemy'}</p>
                            <div className="flex items-end gap-2 mt-1">
                                <span className="text-4xl font-black text-gray-900 dark:text-white leading-none">{opponentReps}</span>
                                <span className="text-sm text-red-600 dark:text-red-300 font-bold mb-1">/ 20</span>
                            </div>
                        </div>
                    )}

                    <div className="text-center">
                        <p className="text-[10px] font-extrabold text-gray-500 dark:text-white/60 uppercase tracking-widest mb-0.5">
                            {(typeof currentExercise === 'string' ? currentExercise : currentExercise?.name || 'EXERCISE').toUpperCase()}
                        </p>
                        <h1 className="text-xl font-black text-gray-900 dark:text-white leading-none uppercase tracking-tighter">
                            {routine?.name || 'Live Session'}
                        </h1>
                    </div>

                    <div className="flex gap-3">
                        <button 
                            onClick={() => setIsVoiceModalVisible(true)}
                            className="w-11 h-11 rounded-full bg-gray-100 dark:bg-white/10 backdrop-blur-md flex items-center justify-center text-primary hover:bg-gray-200 dark:hover:bg-white/20 transition-colors"
                        >
                            <Activity size={24} />
                        </button>
                        <button 
                            onClick={toggleMute}
                            className="w-11 h-11 rounded-full bg-gray-100 dark:bg-white/10 backdrop-blur-md flex items-center justify-center transition-colors hover:bg-gray-200 dark:hover:bg-white/20"
                        >
                            {isMuted ? (
                                <VolumeX size={24} className="text-red-500" />
                            ) : (
                                <Volume2 size={24} className={isAudioEnabled ? 'text-primary' : 'text-gray-900 dark:text-white'} />
                            )}
                        </button>
                    </div>
                </div>
            </div>

            {/* Audio Prompt for Web */}
            {!isAudioEnabled && (
                <div className="relative z-20 flex justify-center mt-4 px-6">
                    <button 
                        onClick={() => setIsAudioEnabled(true)}
                        className="bg-primary text-black px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-widest flex items-center gap-2 shadow-lg animate-bounce"
                    >
                        <Volume2 size={16} />
                        Tap to Enable Voice Coach
                    </button>
                </div>
            )}

            {/* Stats Overlay */}
            <div className="relative z-10 flex gap-4 px-6 mt-6">
                <GlassCard className="flex-1 flex items-center gap-3 py-3 px-4">
                    <div className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-white/5 flex items-center justify-center text-primary">
                        <Clock size={16} />
                    </div>
                    <div>
                        <p className="text-[10px] font-bold text-gray-500 dark:text-white/50 uppercase tracking-tighter">
                            {currentExercise?.type === 'yoga' || ['plank', 'tree'].includes(typeof currentExercise === 'string' ? currentExercise.toLowerCase() : currentExercise?.name?.toLowerCase()) 
                                ? 'Hold Time' 
                                : currentExercise?.type === 'meditation' ? 'Duration' : 'Time'}
                        </p>
                        <p className="text-lg font-black text-gray-900 dark:text-white">
                            {currentExercise?.type === 'yoga' || ['plank', 'tree'].includes(typeof currentExercise === 'string' ? currentExercise.toLowerCase() : currentExercise?.name?.toLowerCase()) 
                                ? `${sessionStats.reps}s` 
                                : formatTime(sessionStats.time)}
                        </p>
                    </div>
                </GlassCard>

                <GlassCard className="flex-1 flex items-center gap-3 py-3 px-4">
                    <div className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-white/5 flex items-center justify-center text-amber-500">
                        <Zap size={16} />
                    </div>
                    <div>
                        <p className="text-[10px] font-bold text-gray-500 dark:text-white/50 uppercase tracking-tighter">Calories</p>
                        <p className="text-lg font-black text-gray-900 dark:text-white">{Math.round(sessionStats.calories)}</p>
                    </div>
                </GlassCard>
            </div>

            {/* Rep Count Overlay */}
            <div className="flex-1 flex flex-col items-center justify-center relative z-10 pointer-events-none">
                <p className="text-2xl font-black text-gray-300 dark:text-white/60 uppercase tracking-[0.2em] mb-2 drop-shadow-lg transition-colors duration-300">
                    {currentExercise?.type === 'yoga' || ['plank', 'tree'].includes(typeof currentExercise === 'string' ? currentExercise.toLowerCase() : currentExercise?.name?.toLowerCase()) 
                        ? 'Holding' 
                        : currentExercise?.type === 'meditation' ? 'Breaths' : 'Reps'}
                </p>
                <h2 className="text-[160px] font-black text-gray-100 dark:text-white leading-none drop-shadow-2xl animate-in zoom-in duration-300 transition-colors duration-300">
                    {sessionStats.reps}{currentExercise?.type === 'yoga' || ['plank', 'tree'].includes(typeof currentExercise === 'string' ? currentExercise.toLowerCase() : currentExercise?.name?.toLowerCase()) ? 's' : ''}
                </h2>
            </div>

            {/* Bottom Controls Overlay */}
            <div className="relative z-10 p-6 space-y-6 bg-gradient-to-t from-white/90 dark:from-black/80 to-transparent transition-colors duration-300">
                {/* Feedback Card */}
                <GlassCard className="p-4 flex flex-col gap-4">
                    <div className="flex items-center justify-between border-b border-gray-200 dark:border-white/5 pb-3">
                        <span className="text-[10px] font-extrabold text-gray-500 dark:text-white/50 uppercase tracking-widest">Form Score</span>
                        <span className={`text-xl font-black ${sessionStats.avgScore > 80 ? 'text-primary' : 'text-red-500'}`}>
                            {sessionStats.avgScore}%
                        </span>
                    </div>
                    <div className="flex items-center gap-3">
                        <Activity size={18} className="text-primary shrink-0" />
                        <p className="text-sm font-bold text-gray-900 dark:text-white/90 leading-tight line-clamp-2 italic">
                            "{advice}"
                        </p>
                    </div>
                </GlassCard>

                {/* Control Buttons */}
                <div className="flex items-center justify-between gap-4">
                    <button 
                        onClick={phase === 'rest' ? resumeWorkout : pauseWorkout}
                        className="w-14 h-14 rounded-full bg-gray-100 dark:bg-white/10 flex items-center justify-center text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-white/20 transition-all active:scale-90"
                    >
                        {phase === 'rest' ? <Play size={24} className="fill-gray-900 dark:fill-white" /> : <Pause size={24} className="fill-gray-900 dark:fill-white" />}
                    </button>

                    <button 
                        onClick={handleComplete}
                        className="flex-1 h-14 bg-primary rounded-2xl flex items-center justify-center gap-2 text-black font-black uppercase tracking-widest hover:brightness-110 transition-all active:scale-[0.98]"
                    >
                        Finish Session
                        <ChevronRight size={20} />
                    </button>

                    <button 
                        onClick={resetWorkout}
                        className="w-14 h-14 rounded-full bg-gray-100 dark:bg-white/10 flex items-center justify-center text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-white/20 transition-all active:scale-90"
                    >
                        <RotateCcw size={24} />
                    </button>
                </div>
            </div>

            {/* Duel Result Overlay */}
            {duelResult && (
                <div className="absolute inset-0 z-50 bg-white/90 dark:bg-black/90 flex flex-col items-center justify-center p-6 animate-in fade-in duration-500 backdrop-blur-sm transition-colors duration-300">
                    <div className="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-white/10 rounded-3xl p-8 max-w-sm w-full text-center relative overflow-hidden shadow-2xl transition-colors duration-300">
                        {/* Background Glow */}
                        <div className={`absolute inset-0 opacity-20 ${duelResult === 'won' ? 'bg-green-500' : 'bg-red-500'} blur-3xl`} />
                        
                        <div className="relative z-10">
                            {duelResult === 'won' ? (
                                <div className="w-24 h-24 rounded-full bg-green-100 dark:bg-green-500/20 flex items-center justify-center mx-auto mb-6 animate-bounce">
                                    <Trophy size={48} className="text-green-600 dark:text-green-500" />
                                </div>
                            ) : (
                                <div className="w-24 h-24 rounded-full bg-red-100 dark:bg-red-500/20 flex items-center justify-center mx-auto mb-6">
                                    <Frown size={48} className="text-red-600 dark:text-red-500" />
                                </div>
                            )}

                            <h2 className="text-4xl font-black text-gray-900 dark:text-white mb-2 uppercase italic tracking-tighter drop-shadow-lg">
                                {duelResult === 'won' ? 'Victory!' : 'Defeat'}
                            </h2>
                            <p className="text-gray-500 dark:text-white/60 mb-8 font-medium text-lg">
                                {duelResult === 'won' 
                                    ? `You crushed ${opponent?.username || 'your opponent'}!` 
                                    : `${opponent?.username || 'Opponent'} was faster this time.`}
                            </p>

                            <button 
                                onClick={handleComplete}
                                className={`w-full py-4 rounded-xl font-black uppercase tracking-widest text-sm transition-transform active:scale-95 shadow-lg ${
                                    duelResult === 'won' 
                                        ? 'bg-green-500 text-black hover:bg-green-400' 
                                        : 'bg-red-500 text-white hover:bg-red-600'
                                }`}
                            >
                                Continue to Summary
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <VoiceModal
                visible={isVoiceModalVisible}
                onClose={() => setIsVoiceModalVisible(false)}
                onSubmit={handleVoiceSubmit}
            />
        </div>
    );
};

export default LiveWorkout;
