import React from 'react';
import { Swords, X, Check } from 'lucide-react';
import GlassCard from './GlassCard';

const DuelInviteModal = ({ invite, onAccept, onDecline }) => {
  if (!invite) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
      <GlassCard className="w-full max-w-sm mx-4 p-6 border-orange-500 neon-border flex flex-col items-center text-center bg-white/90 dark:bg-zinc-900/90 transition-colors duration-300">
        <div className="w-16 h-16 rounded-full bg-orange-500/20 flex items-center justify-center mb-4 animate-pulse">
          <Swords size={32} className="text-orange-500" />
        </div>
        
        <h2 className="text-2xl font-black mb-2 text-gray-900 dark:text-white transition-colors duration-300">Duel Challenge!</h2>
        <p className="text-gray-600 dark:text-zinc-400 mb-6 transition-colors duration-300">
          <span className="text-gray-900 dark:text-white font-bold transition-colors duration-300">{invite.from}</span> wants to challenge you to a <span className="text-orange-500 font-bold">{invite.exercise}</span> duel!
        </p>

        <div className="flex gap-4 w-full">
          <button
            onClick={onDecline}
            className="flex-1 py-3 px-4 rounded-xl bg-gray-100 dark:bg-zinc-800 text-gray-600 dark:text-zinc-400 font-bold hover:bg-gray-200 dark:hover:bg-zinc-700 transition-colors duration-300 flex items-center justify-center gap-2"
          >
            <X size={18} />
            Decline
          </button>
          <button
            onClick={() => onAccept(invite)}
            className="flex-1 py-3 px-4 rounded-xl bg-gradient-to-r from-orange-500 to-red-600 text-white font-bold hover:scale-105 transition-transform flex items-center justify-center gap-2 shadow-lg shadow-orange-500/20"
          >
            <Check size={18} />
            Accept
          </button>
        </div>
      </GlassCard>
    </div>
  );
};

export default DuelInviteModal;
