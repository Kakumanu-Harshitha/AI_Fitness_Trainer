import React from 'react';
import { Droplets, Plus, Minus } from 'lucide-react';
import GlassCard from './GlassCard';
import ProgressRing from './ProgressRing';

const WaterTrackerCard = ({ current, goal, onAdd, onRemove }) => {
  const progress = Math.min(current / goal, 1);

  return (
    <GlassCard className="mb-6" neonBorder neonColor="#3b82f6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-blue-500/15 flex items-center justify-center">
          <Droplets size={20} className="text-blue-500" />
        </div>
        <div className="flex-1">
          <p className="text-[10px] font-extrabold tracking-wider text-blue-500 uppercase">WATER INTAKE</p>
          <p className="text-lg font-black text-gray-900 dark:text-white transition-colors duration-300">{current} / {goal} ml</p>
        </div>
        
        <div className="flex gap-2">
          <button 
            onClick={() => onRemove && onRemove(250)}
            className="w-9 h-9 rounded-lg bg-blue-500/10 dark:bg-blue-500/20 border border-blue-500/20 dark:border-blue-500/30 flex items-center justify-center hover:bg-blue-500/20 dark:hover:bg-blue-500/30 transition-colors"
          >
            <Minus size={20} className="text-blue-600 dark:text-blue-400" />
          </button>
          
          <button 
            onClick={() => onAdd(250)}
            className="w-9 h-9 rounded-lg bg-blue-500 flex items-center justify-center hover:opacity-90 transition-opacity shadow-lg shadow-blue-500/20"
          >
            <Plus size={20} className="text-white" />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-5">
        <ProgressRing
          progress={progress * 100}
          size={80}
          strokeWidth={8}
          color="#3b82f6"
        >
          <span className="text-sm font-extrabold text-gray-900 dark:text-white transition-colors duration-300">{Math.round(progress * 100)}%</span>
        </ProgressRing>
        <div className="flex-1">
          <h3 className="text-base font-bold text-gray-900 dark:text-white mb-1 transition-colors duration-300">Stay Hydrated</h3>
          <p className="text-xs text-zinc-500 leading-relaxed">Drinking water improves focus and performance.</p>
        </div>
      </div>
    </GlassCard>
  );
};

export default WaterTrackerCard;
