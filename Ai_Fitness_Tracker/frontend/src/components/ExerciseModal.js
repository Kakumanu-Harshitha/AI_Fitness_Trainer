import React, { useState } from 'react';
import { X } from 'lucide-react';

/**
 * Exercise Modal Component
 * Enhanced exercise selection modal with search and category filters
 */
const ExerciseModal = ({ visible, onClose, onSelectExercise, selectedIds = [] }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', name: 'All', icon: '💪' },
    { id: 'upper', name: 'Upper', icon: '🦾' },
    { id: 'lower', name: 'Lower', icon: '🦵' },
    { id: 'core', name: 'Core', icon: '🎯' },
    { id: 'cardio', name: 'Cardio', icon: '🔥' },
  ];

  const exercises = [
    { id: 1, name: 'Squats', category: 'lower', reps: 15, duration: 60, icon: '🦵', difficulty: 'medium', description: 'Build leg strength and power' },
    { id: 2, name: 'Push-ups', category: 'upper', reps: 12, duration: 45, icon: '💪', difficulty: 'medium', description: 'Upper body strength' },
    { id: 3, name: 'Lunges', category: 'lower', reps: 10, duration: 50, icon: '🏃', difficulty: 'medium', description: 'Leg and glute activation' },
    { id: 4, name: 'Plank', category: 'core', reps: 1, duration: 60, icon: '🧘', difficulty: 'hard', description: 'Core stability and endurance' },
    { id: 5, name: 'Burpees', category: 'cardio', reps: 10, duration: 40, icon: '🔥', difficulty: 'hard', description: 'Full body cardio blast' },
    { id: 6, name: 'Mountain Climbers', category: 'cardio', reps: 20, duration: 45, icon: '⛰️', difficulty: 'hard', description: 'High intensity cardio' },
    { id: 7, name: 'Jumping Jacks', category: 'cardio', reps: 30, duration: 30, icon: '🤸', difficulty: 'easy', description: 'Warm up and cardio' },
    { id: 8, name: 'Sit-ups', category: 'core', reps: 15, duration: 40, icon: '🎯', difficulty: 'easy', description: 'Abdominal focus' },
  ];

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return '#22c55e';
      case 'medium': return '#B4FF39';
      case 'hard': return '#ef4444';
      default: return '#B4FF39';
    }
  };

  const filteredExercises = exercises.filter(ex => {
    const matchesSearch = ex.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || ex.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-300">
      <div className="bg-white dark:bg-zinc-950 w-full max-w-2xl max-h-[90vh] overflow-hidden rounded-[32px] border border-gray-200 dark:border-zinc-800 flex flex-col animate-in slide-in-from-bottom duration-500 transition-colors duration-300">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-zinc-900 flex justify-between items-center">
          <h2 className="text-xl font-black text-gray-900 dark:text-white">Exercise Library</h2>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-zinc-900 rounded-full transition-colors"
          >
            <X size={24} className="text-gray-500 dark:text-zinc-400" />
          </button>
        </div>

        {/* Search */}
        <div className="px-6 py-4">
          <input
            type="text"
            placeholder="Search exercises..."
            className="w-full bg-gray-100 dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-xl p-3 text-gray-900 dark:text-white focus:outline-none focus:border-primary transition-colors"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Categories */}
        <div className="px-6 flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl whitespace-nowrap transition-all border ${
                selectedCategory === cat.id 
                  ? 'bg-primary/10 border-primary text-primary' 
                  : 'bg-gray-100 dark:bg-zinc-900 border-gray-200 dark:border-zinc-800 text-gray-500 dark:text-zinc-400'
              }`}
            >
              <span>{cat.icon}</span>
              <span className="text-sm font-bold">{cat.name}</span>
            </button>
          ))}
        </div>

        {/* Exercise Grid */}
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {filteredExercises.map((exercise) => (
            <button
              key={exercise.id}
              onClick={() => onSelectExercise(exercise)}
              className={`text-left p-4 rounded-2xl border transition-all ${
                selectedIds.includes(exercise.id)
                  ? 'bg-primary/5 border-primary'
                  : 'bg-gray-50 dark:bg-zinc-900/50 border-gray-200 dark:border-zinc-800 hover:border-gray-300 dark:hover:border-zinc-700'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-2xl">{exercise.icon}</span>
                <span 
                  className="text-[10px] font-black uppercase px-2 py-1 rounded-lg"
                  style={{ 
                    backgroundColor: `${getDifficultyColor(exercise.difficulty)}20`,
                    color: getDifficultyColor(exercise.difficulty)
                  }}
                >
                  {exercise.difficulty}
                </span>
              </div>
              <h3 className="font-bold text-white mb-1">{exercise.name}</h3>
              <p className="text-xs text-zinc-500 mb-3 line-clamp-2">{exercise.description}</p>
              <div className="flex items-center gap-2 text-[10px] font-black text-zinc-400 uppercase">
                <span>{exercise.reps} reps</span>
                <span className="text-zinc-700">•</span>
                <span>{exercise.duration}s</span>
              </div>
            </button>
          ))}
          {filteredExercises.length === 0 && (
            <div className="col-span-full py-12 text-center text-zinc-500">
              No exercises found matching your search.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExerciseModal;
