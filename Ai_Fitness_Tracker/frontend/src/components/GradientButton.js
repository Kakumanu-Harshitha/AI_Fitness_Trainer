import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const GradientButton = ({
  onPress,
  onClick, // Support standard onClick prop
  title,
  children, // Support children
  colors,
  textColor = 'text-black',
  loading = false,
  disabled = false,
  className
}) => {
  const activeColors = colors || ['#B4FF39', '#85cc2a'];
  
  return (
    <button
      onClick={onPress || onClick}
      disabled={disabled || loading}
      className={twMerge(
        'relative overflow-hidden rounded-2xl transition-all active:scale-95 disabled:opacity-70 disabled:active:scale-100 disabled:cursor-not-allowed',
        className
      )}
    >
      <div 
        className="py-4 px-6 flex items-center justify-center font-black text-base transition-colors"
        style={{ 
          background: disabled 
            ? undefined 
            : `linear-gradient(to right, ${activeColors[0]}, ${activeColors[1]})`,
        }}
      >
        <div className={`absolute inset-0 -z-10 ${disabled ? 'bg-gray-300 dark:bg-zinc-800' : ''}`} />
        
        {loading ? (
          <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
        ) : (
          children ? children : <span className={disabled ? 'text-gray-500 dark:text-zinc-500' : textColor}>{title}</span>
        )}
      </div>
    </button>
  );
};

export default GradientButton;
