import React from 'react';
import { Utensils, Zap, Activity, Info } from 'lucide-react';
import GlassCard from './GlassCard';

const DietPlanCard = ({ dietPlan }) => {
  if (!dietPlan) return null;

  return (
    <GlassCard className="p-6 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />
      
      <div className="flex items-center gap-3 mb-6 relative z-10">
        <div className="p-3 bg-green-500/10 dark:bg-green-500/20 rounded-xl transition-colors duration-300">
          <Utensils className="text-green-600 dark:text-green-500" size={24} />
        </div>
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white transition-colors duration-300">Smart Diet Plan</h3>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">Personalized for your goal</p>
        </div>
      </div>

      <div className="space-y-4 relative z-10">
        {/* Pre-Workout */}
        <div className="p-4 bg-zinc-50 dark:bg-zinc-900/50 rounded-xl border border-zinc-200 dark:border-white/5 transition-all duration-300 hover:border-green-500/30">
          <div className="flex items-center gap-2 mb-2">
            <Zap size={16} className="text-yellow-500" />
            <span className="text-sm font-bold text-gray-700 dark:text-zinc-300">Pre-Workout Fuel</span>
          </div>
          <p className="text-sm text-gray-600 dark:text-zinc-400">{dietPlan.pre_workout}</p>
        </div>

        {/* Post-Workout */}
        <div className="p-4 bg-zinc-50 dark:bg-zinc-900/50 rounded-xl border border-zinc-200 dark:border-white/5 transition-all duration-300 hover:border-blue-500/30">
          <div className="flex items-center gap-2 mb-2">
            <Activity size={16} className="text-blue-500" />
            <span className="text-sm font-bold text-gray-700 dark:text-zinc-300">Post-Workout Recovery</span>
          </div>
          <p className="text-sm text-gray-600 dark:text-zinc-400">{dietPlan.post_workout}</p>
        </div>

        {/* Analysis & Tips */}
        <div className="p-4 bg-zinc-50 dark:bg-zinc-900/50 rounded-xl border border-zinc-200 dark:border-white/5 transition-all duration-300 hover:border-purple-500/30">
          <div className="flex items-center gap-2 mb-2">
            <Info size={16} className="text-purple-500" />
            <span className="text-sm font-bold text-gray-700 dark:text-zinc-300">Analysis & Tips</span>
          </div>
          <p className="text-sm text-gray-600 dark:text-zinc-400 mb-2">{dietPlan.analysis}</p>
          <div className="h-px bg-zinc-200 dark:bg-white/10 my-2" />
          <p className="text-xs text-zinc-500 italic">"{dietPlan.management_suggestion}"</p>
        </div>
      </div>
    </GlassCard>
  );
};

export default DietPlanCard;
