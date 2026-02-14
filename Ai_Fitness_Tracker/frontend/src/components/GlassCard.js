import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const GlassCard = ({ children, className, neonBorder = false, neonColor }) => {
  const borderColor = neonColor || '#B4FF39';

  return (
    <div
      className={twMerge(
        'glass-card p-5 border border-border transition-all duration-300',
        neonBorder && 'neon-border',
        className
      )}
      style={neonBorder ? { borderColor: borderColor, boxShadow: `0px 0px 12px ${borderColor}33` } : {}}
    >
      {children}
    </div>
  );
};

export default GlassCard;
