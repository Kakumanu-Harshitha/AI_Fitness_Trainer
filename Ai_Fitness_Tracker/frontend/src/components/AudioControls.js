import React from 'react';
import { Volume2, VolumeX } from 'lucide-react';

/**
 * Audio Controls Component
 * Toggle for audio cues and voice coach during workouts
 */
const AudioControls = ({
  audioCuesEnabled = true,
  voiceCoachEnabled = true,
  onToggleAudioCues,
  onToggleVoiceCoach
}) => {
  return (
    <div className="flex flex-row gap-3 p-4 animate-in fade-in duration-500">
      {/* Audio Cues Toggle */}
      <button
        className={`flex flex-row items-center gap-2 py-2.5 px-4 rounded-2xl bg-gray-100 dark:bg-white/5 border-2 transition-all ${
          audioCuesEnabled ? 'bg-primary/15 border-primary' : 'border-transparent'
        }`}
        onClick={onToggleAudioCues}
      >
        {audioCuesEnabled ? (
          <Volume2 size={20} className="text-primary" />
        ) : (
          <VolumeX size={20} className="text-gray-500 dark:text-zinc-500" />
        )}
        <span className={`text-[13px] font-bold ${
          audioCuesEnabled ? 'text-primary' : 'text-gray-500 dark:text-zinc-500'
        }`}>
          Audio Cues
        </span>
      </button>

      {/* Voice Coach Toggle */}
      <button
        className={`flex flex-row items-center gap-2 py-2.5 px-4 rounded-2xl bg-gray-100 dark:bg-white/5 border-2 transition-all ${
          voiceCoachEnabled ? 'bg-primary/15 border-primary' : 'border-transparent'
        }`}
        onClick={onToggleVoiceCoach}
      >
        <span className="text-lg">🎙️</span>
        <span className={`text-[13px] font-bold ${
          voiceCoachEnabled ? 'text-primary' : 'text-gray-500 dark:text-zinc-500'
        }`}>
          Voice Coach
        </span>
      </button>
    </div>
  );
};

export default AudioControls;
