import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, 
  Dumbbell, 
  Clock, 
  Zap, 
  X, 
  Play, 
  Trash2, 
  Eye, 
  GripVertical,
  ChevronUp,
  ChevronDown
} from 'lucide-react';
import GlassCard from '../components/GlassCard';
import GradientButton from '../components/GradientButton';
import ExerciseModal from '../components/ExerciseModal';
import { useApi } from '../hooks/useApi';

const Workouts = () => {
  const { get, post, del } = useApi();
  const navigate = useNavigate();
  const [routines, setRoutines] = useState([]);
  const [showRoutineModal, setShowRoutineModal] = useState(false);
  const [showExerciseLibrary, setShowExerciseLibrary] = useState(false);
  const [routineName, setRoutineName] = useState('');
  const [selectedExercises, setSelectedExercises] = useState([]);
  const [complexity, setComplexity] = useState('BALANCED');
  const [visionComplexity, setVisionComplexity] = useState('NORMAL');
  const [isSaving, setIsSaving] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('fitness'); // 'fitness' or 'mindfulness'

  const visionComplexityLevels = [
    { id: 'BASIC', name: 'Basic', description: 'Pose detection only', color: '#94a3b8' },
    { id: 'NORMAL', name: 'Normal', description: 'Pose + Form analysis', color: '#B4FF39' },
    { id: 'ADVANCED', name: 'Advanced', description: 'Real-time velocity & depth', color: '#f59e0b' }
  ];

  const complexityLevels = [
    { id: 'LITE', name: 'Lite', color: '#22c55e' },
    { id: 'BALANCED', name: 'Balanced', color: '#B4FF39' },
    { id: 'HEAVY', name: 'Heavy', color: '#f97316' }
  ];

  const availableExercises = [
    { id: 1, name: 'Squats', reps: 15, duration: 60, icon: '🦵' },
    { id: 2, name: 'Push-ups', reps: 12, duration: 45, icon: '💪' },
    { id: 3, name: 'Lunges', reps: 10, duration: 50, icon: '🏃' },
    { id: 4, name: 'Plank', reps: 1, duration: 60, icon: '🧘' },
    { id: 5, name: 'Burpees', reps: 10, duration: 40, icon: '🔥' },
    { id: 6, name: 'Mountain Climbers', reps: 20, duration: 45, icon: '⛰️' },
    { id: 7, name: 'Jumping Jacks', reps: 30, duration: 30, icon: '🤸' },
    { id: 8, name: 'Sit-ups', reps: 15, duration: 40, icon: '🎯' },
  ];

  const mindfulnessExercises = [
    { id: 'm1', name: 'Warrior II', type: 'yoga', duration: 300, icon: '🧘‍♀️', description: 'Strengthen legs and open hips' },
    { id: 'm2', name: 'Tree Pose', type: 'yoga', duration: 180, icon: '🌲', description: 'Improve balance and focus' },
    { id: 'm3', name: 'Breath Focus', type: 'meditation', duration: 300, icon: '🌬️', description: 'Calm mind and regulate breath' },
  ];

  useEffect(() => {
    fetchRoutines();
  }, []);

  const fetchRoutines = async () => {
    try {
      setLoading(true);
      const data = await get('/routines/');
      if (Array.isArray(data)) {
        setRoutines(data);
      }
    } catch (error) {
      console.error('Fetch routines failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRoutine = () => {
    setRoutineName('');
    setSelectedExercises([]);
    setComplexity('BALANCED');
    setVisionComplexity('NORMAL');
    setShowRoutineModal(true);
  };

  const handleLoadTemplate = (templateName) => {
    setRoutineName(templateName);
    setComplexity('BALANCED');
    setVisionComplexity('NORMAL');
    
    let exercises = [];
    const timestamp = Date.now();
    if (templateName === 'Full Body') {
      exercises = [
        { ...availableExercises[0], uniqueId: `1-${timestamp}-1` },
        { ...availableExercises[1], uniqueId: `2-${timestamp}-2` },
        { ...availableExercises[2], uniqueId: `3-${timestamp}-3` }
      ];
    } else if (templateName === 'Upper Body') {
      exercises = [
        { ...availableExercises[1], uniqueId: `2-${timestamp}-1` },
        { ...availableExercises[4], uniqueId: `5-${timestamp}-2` },
        { ...availableExercises[7], uniqueId: `8-${timestamp}-3` }
      ];
    } else if (templateName === 'Lower Body') {
      exercises = [
        { ...availableExercises[0], uniqueId: `1-${timestamp}-1` },
        { ...availableExercises[2], uniqueId: `3-${timestamp}-2` },
        { ...availableExercises[5], uniqueId: `6-${timestamp}-3` }
      ];
    } else if (templateName === 'Core Focus') {
      exercises = [
        { ...availableExercises[3], uniqueId: `4-${timestamp}-1` },
        { ...availableExercises[7], uniqueId: `8-${timestamp}-2` },
        { ...availableExercises[6], uniqueId: `7-${timestamp}-3` }
      ];
    }
    
    setSelectedExercises(exercises);
    setShowRoutineModal(true);
  };

  const addExercise = (exercise) => {
    const newExercise = { 
      ...exercise, 
      uniqueId: Date.now().toString() + Math.random() 
    };
    setSelectedExercises(prev => [...prev, newExercise]);
    setShowExerciseLibrary(false);
  };

  const removeExercise = (uniqueId) => {
    setSelectedExercises(prev => prev.filter(e => e.uniqueId !== uniqueId));
  };

  const updateDuration = (uniqueId, delta) => {
    setSelectedExercises(prev => prev.map(e => {
      if (e.uniqueId === uniqueId) {
        const newDuration = Math.max(10, e.duration + delta);
        return { ...e, duration: newDuration };
      }
      return e;
    }));
  };

  const addRestPeriod = () => {
    setSelectedExercises(prev => [
      ...prev,
      {
        id: 'rest',
        uniqueId: Date.now().toString(),
        name: 'Rest',
        duration: 30,
        icon: '☕',
        isRest: true
      }
    ]);
  };

  const moveExercise = (index, direction) => {
    const newExercises = [...selectedExercises];
    const newIndex = index + direction;
    if (newIndex >= 0 && newIndex < newExercises.length) {
      const [movedItem] = newExercises.splice(index, 1);
      newExercises.splice(newIndex, 0, movedItem);
      setSelectedExercises(newExercises);
    }
  };

  const handleSaveRoutine = async () => {
    if (!routineName) {
      alert('Please enter a routine name');
      return;
    }
    if (selectedExercises.length === 0) {
      alert('Please add at least one exercise');
      return;
    }

    setIsSaving(true);
    const newRoutine = {
      name: routineName,
      description: `Intensity: ${complexity}, Vision: ${visionComplexity}`,
      complexity: complexity,
      vision_complexity: visionComplexity,
      steps: selectedExercises.map((ex, idx) => ({
        exercise_id: ex.isRest ? 'rest' : ex.name.toLowerCase().replace(/\s+/g, '_'),
        exercise_name: ex.name,
        reps: ex.reps || 0,
        sets: 1,
        duration_seconds: ex.duration,
        order_index: idx,
        icon: ex.icon
      }))
    };

    try {
      const result = await post('/routines/', newRoutine);
      if (result) {
        await fetchRoutines();
        setShowRoutineModal(false);
      }
    } catch (error) {
      console.error('Save routine failed:', error);
      // Fallback for demo
      const mockRoutine = { 
        ...newRoutine, 
        id: Date.now().toString(),
        totalDuration: selectedExercises.reduce((sum, ex) => sum + ex.duration, 0)
      };
      setRoutines(prev => [...prev, mockRoutine]);
      setShowRoutineModal(false);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteRoutine = async (routineId) => {
    if (!window.confirm('Are you sure you want to delete this routine?')) return;
    try {
      await del(`/routines/${routineId}`);
      setRoutines(prev => prev.filter(r => r.id !== routineId));
    } catch (error) {
      console.error('Delete routine failed:', error);
      setRoutines(prev => prev.filter(r => r.id !== routineId));
    }
  };

  const calculateTotalDuration = (routine) => {
    if (routine.totalDuration) return routine.totalDuration;
    if (routine.steps) return routine.steps.reduce((acc, step) => acc + (step.duration_seconds || 0), 0);
    return 0;
  };

  const handleStartMindfulness = (exercise) => {
    navigate('/live-workout', {
      state: {
        routine: {
          id: `mind-${exercise.id}`,
          name: exercise.name,
          exercises: [exercise],
          type: 'mindfulness'
        }
      }
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-black text-gray-900 dark:text-white p-6 pb-24 max-w-2xl mx-auto transition-colors duration-300">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-black">Workouts</h1>
          <p className="text-gray-500 dark:text-zinc-400 text-sm">Choose your training path</p>
        </div>
        <button 
          onClick={handleCreateRoutine}
          className="bg-primary text-black px-4 py-2 rounded-xl font-bold flex items-center gap-2 hover:scale-105 transition-transform active:scale-95"
        >
          <Plus size={20} />
          <span>New Routine</span>
        </button>
      </div>

      {/* Mode Switcher */}
      <div className="flex p-1 bg-gray-200 dark:bg-zinc-900/50 rounded-xl mb-8 w-fit transition-colors">
        <button
          onClick={() => setActiveTab('fitness')}
          className={`px-6 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'fitness' 
              ? 'bg-[#B4FF39] text-black shadow-lg shadow-[#B4FF39]/20' 
              : 'text-gray-500 dark:text-zinc-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          Fitness
        </button>
        <button
          onClick={() => setActiveTab('mindfulness')}
          className={`px-6 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'mindfulness' 
              ? 'bg-[#B4FF39] text-black shadow-lg shadow-[#B4FF39]/20' 
              : 'text-gray-500 dark:text-zinc-400 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          Yoga & Mind
        </button>
      </div>

      {activeTab === 'mindfulness' ? (
        <div className="grid grid-cols-1 gap-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {mindfulnessExercises.map((exercise) => (
            <GlassCard key={exercise.id} className="p-6 relative group overflow-hidden">
               <div className="absolute top-0 right-0 w-32 h-32 bg-[#B4FF39]/5 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-[#B4FF39]/10 transition-colors" />
               
               <div className="flex justify-between items-start mb-4">
                 <div className="w-12 h-12 bg-gray-100 dark:bg-zinc-800 rounded-xl flex items-center justify-center text-2xl transition-colors">
                   {exercise.icon}
                 </div>
                 <span className="px-3 py-1 bg-gray-100 dark:bg-zinc-800 rounded-full text-xs text-gray-500 dark:text-zinc-400 transition-colors">
                   {Math.floor(exercise.duration / 60)} min
                 </span>
               </div>

               <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{exercise.name}</h3>
               <p className="text-sm text-gray-500 dark:text-zinc-400 mb-6">{exercise.description}</p>

               <GradientButton 
                 onPress={() => handleStartMindfulness(exercise)}
                 className="w-full"
                 title="Start Session"
               />
            </GlassCard>
          ))}
        </div>
      ) : (
        <>
          {/* Quick Start Templates */}
          <div className="mb-8">
        <h2 className="text-sm font-extrabold text-gray-500 dark:text-zinc-500 uppercase tracking-widest mb-4">Quick Start</h2>
        <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide">
          {['Full Body', 'Upper Body', 'Lower Body', 'Core Focus'].map((template, index) => (
            <button 
              key={index} 
              onClick={() => handleLoadTemplate(template)}
              className="min-w-[140px] bg-gray-200 dark:bg-zinc-900/50 border border-gray-300 dark:border-zinc-800 p-4 rounded-2xl flex flex-col items-center gap-2 hover:border-primary/50 transition-colors"
            >
              <Zap size={24} className="text-primary" />
              <span className="font-bold whitespace-nowrap text-gray-900 dark:text-white">{template}</span>
              <span className="text-[10px] text-gray-500 dark:text-zinc-500">15 min</span>
            </button>
          ))}
        </div>
      </div>

      {/* My Routines */}
      <div>
        <h2 className="text-sm font-extrabold text-gray-500 dark:text-zinc-500 uppercase tracking-widest mb-4">My Routines</h2>
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : routines.length === 0 ? (
          <GlassCard className="flex flex-col items-center justify-center py-12 text-center">
            <Dumbbell size={48} className="text-gray-400 dark:text-zinc-700 mb-4" />
            <p className="font-bold text-gray-500 dark:text-zinc-400">No routines yet</p>
            <p className="text-sm text-gray-400 dark:text-zinc-600">Create your first workout routine</p>
          </GlassCard>
        ) : (
          <div className="space-y-4">
            {routines.map((routine) => (
              <GlassCard key={routine.id} className="group">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
                    <Dumbbell size={20} className="text-primary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900 dark:text-white">{routine.name}</h3>
                    <p className="text-xs text-gray-500 dark:text-zinc-500">
                      {(routine.exercises?.length || routine.steps?.length || 0)} exercises • {Math.floor(calculateTotalDuration(routine) / 60)} min
                    </p>
                  </div>
                  <button
                    onClick={() => navigate('/live-workout', { state: { routineId: routine.id } })}
                    className="w-10 h-10 rounded-full bg-primary flex items-center justify-center hover:scale-110 transition-transform active:scale-95"
                  >
                    <Play size={16} className="text-black fill-black ml-0.5" />
                  </button>
                  <button
                    onClick={() => handleDeleteRoutine(routine.id)}
                    className="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center hover:bg-red-500/20 transition-colors"
                  >
                    <Trash2 size={16} className="text-red-500" />
                  </button>
                </div>
              </GlassCard>
            ))}
          </div>
        )}
      </div>
      </>
      )}

      {/* Create Routine Modal */}
      {showRoutineModal && (
        <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center bg-black/80 backdrop-blur-sm p-0 sm:p-4">
          <div className="bg-white dark:bg-zinc-950 w-full max-w-2xl max-h-[90vh] overflow-hidden rounded-t-[32px] sm:rounded-[32px] border border-gray-200 dark:border-zinc-800 flex flex-col animate-in slide-in-from-bottom duration-300 transition-colors">
            {/* Modal Header */}
            <div className="p-6 border-b border-gray-200 dark:border-zinc-900 flex justify-between items-center transition-colors">
              <h2 className="text-xl font-black text-gray-900 dark:text-white">Create Routine</h2>
              <button onClick={() => setShowRoutineModal(false)} className="p-2 hover:bg-gray-100 dark:hover:bg-zinc-900 rounded-full transition-colors">
                <X size={24} className="text-gray-500 dark:text-zinc-400" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-8">
              {/* Routine Name */}
              <div className="space-y-2">
                <label className="text-xs font-extrabold text-gray-500 dark:text-zinc-500 uppercase tracking-widest">Routine Name</label>
                <input
                  type="text"
                  placeholder="e.g., Morning Burn"
                  className="w-full bg-gray-50 dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-xl p-4 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors"
                  value={routineName}
                  onChange={(e) => setRoutineName(e.target.value)}
                />
              </div>

              {/* Intensity Level */}
              <div className="space-y-4">
                <label className="text-xs font-extrabold text-gray-500 dark:text-zinc-500 uppercase tracking-widest">Workout Intensity</label>
                <div className="grid grid-cols-3 gap-3">
                  {complexityLevels.map((level) => (
                    <button
                      key={level.id}
                      onClick={() => setComplexity(level.id)}
                      className={`py-3 rounded-xl border font-bold transition-all ${
                        complexity === level.id 
                          ? 'border-primary bg-primary/10 text-primary' 
                          : 'border-gray-200 dark:border-zinc-800 bg-gray-50 dark:bg-zinc-900 text-gray-500 dark:text-zinc-500'
                      }`}
                    >
                      {level.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* AI Vision Complexity */}
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Eye size={16} className="text-gray-500 dark:text-zinc-500" />
                  <label className="text-xs font-extrabold text-gray-500 dark:text-zinc-500 uppercase tracking-widest">AI Vision Analysis</label>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {visionComplexityLevels.map((level) => (
                    <button
                      key={level.id}
                      onClick={() => setVisionComplexity(level.id)}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        visionComplexity === level.id 
                          ? 'border-primary bg-primary/10' 
                          : 'border-gray-200 dark:border-zinc-800 bg-gray-50 dark:bg-zinc-900'
                      }`}
                    >
                      <p className={`text-xs font-black uppercase mb-1 ${visionComplexity === level.id ? 'text-primary' : 'text-gray-400 dark:text-zinc-400'}`}>
                        {level.name}
                      </p>
                      <p className="text-[10px] text-gray-500 dark:text-zinc-500 leading-tight">{level.description}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Workout Sequence */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-extrabold text-gray-500 dark:text-zinc-500 uppercase tracking-widest">
                    Sequence ({selectedExercises.length})
                  </label>
                  <button 
                    onClick={addRestPeriod}
                    className="flex items-center gap-1.5 bg-primary text-black px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-tighter"
                  >
                    <Clock size={12} />
                    Add Rest
                  </button>
                </div>

                <div className="space-y-2">
                  {selectedExercises.map((exercise, index) => (
                    <div key={exercise.uniqueId} className="bg-gray-50 dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-xl p-3 flex items-center gap-3 transition-colors">
                      <div className="flex flex-col gap-1">
                        <button 
                          disabled={index === 0}
                          onClick={() => moveExercise(index, -1)}
                          className="text-gray-400 dark:text-zinc-600 disabled:opacity-30 hover:text-gray-900 dark:hover:text-white transition-colors"
                        >
                          <ChevronUp size={16} />
                        </button>
                        <button 
                          disabled={index === selectedExercises.length - 1}
                          onClick={() => moveExercise(index, 1)}
                          className="text-gray-400 dark:text-zinc-600 disabled:opacity-30 hover:text-gray-900 dark:hover:text-white transition-colors"
                        >
                          <ChevronDown size={16} />
                        </button>
                      </div>
                      <span className="text-xl">{exercise.icon}</span>
                      <div className="flex-1">
                        <p className="font-bold text-sm text-gray-900 dark:text-white">{exercise.name}</p>
                        <p className="text-[10px] text-gray-500 dark:text-zinc-500 uppercase font-black">{exercise.duration}s</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => updateDuration(exercise.uniqueId, -5)}
                          className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center font-black text-zinc-400 hover:text-white"
                        >
                          -
                        </button>
                        <button 
                          onClick={() => updateDuration(exercise.uniqueId, 5)}
                          className="w-8 h-8 rounded-lg bg-zinc-800 flex items-center justify-center font-black text-zinc-400 hover:text-white"
                        >
                          +
                        </button>
                        <button 
                          onClick={() => removeExercise(exercise.uniqueId)}
                          className="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center text-red-500"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                  {selectedExercises.length === 0 && (
                    <div className="py-8 text-center border-2 border-dashed border-zinc-900 rounded-2xl">
                      <p className="text-xs text-zinc-600">Add exercises from the library below</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Add Exercise Trigger */}
              <div className="space-y-4">
                <label className="text-xs font-extrabold text-zinc-500 uppercase tracking-widest">Add Exercise</label>
                <button
                  onClick={() => setShowExerciseLibrary(true)}
                  className="w-full bg-zinc-900 border border-zinc-800 border-dashed py-6 rounded-xl flex flex-col items-center gap-2 hover:border-primary/50 transition-colors group"
                >
                  <Plus size={24} className="text-zinc-600 group-hover:text-primary transition-colors" />
                  <span className="text-xs font-bold text-zinc-500 group-hover:text-primary transition-colors">Browse Exercise Library</span>
                </button>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-zinc-900">
              <GradientButton
                onPress={handleSaveRoutine}
                disabled={isSaving}
                className="w-full"
                title={isSaving ? 'Saving...' : 'Save Routine'}
              />
            </div>
          </div>
        </div>
      )}

      {/* Exercise Library Modal */}
      <ExerciseModal 
        visible={showExerciseLibrary}
        onClose={() => setShowExerciseLibrary(false)}
        onSelectExercise={addExercise}
      />
    </div>
  );
};

export default Workouts;
