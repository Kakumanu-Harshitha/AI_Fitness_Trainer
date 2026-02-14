import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const GradientButton = ({
  onPress,
  title,
  colors,
  textColor = 'text-black',
  loading = false,
  disabled = false,
  className
}) => {
  const activeColors = colors || ['#B4FF39', '#85cc2a'];
  
  return (
    <button
      onClick={onPress}
      disabled={disabled || loading}
      className={twMerge(
        'relative overflow-hidden rounded-2xl transition-all active:scale-95 disabled:opacity-50 disabled:active:scale-100',
        className
      )}
    >
      <div 
        className="py-4 px-6 flex items-center justify-center font-black text-base"
        style={{ 
          background: disabled 
            ? 'linear-gradient(to right, #3f3f46, #27272a)' 
            : `linear-gradient(to right, ${activeColors[0]}, ${activeColors[1]})`,
          color: disabled ? '#71717a' : 'inherit'
        }}
      >
        {loading ? (
          <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
        ) : (
          <span className={textColor}>{title}</span>
        )}
      </div>
    </button>
  );
};

export default GradientButton;
