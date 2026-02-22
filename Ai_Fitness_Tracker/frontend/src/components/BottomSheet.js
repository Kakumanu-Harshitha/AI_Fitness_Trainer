import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';

/**
 * Bottom Sheet Component
 * Reusable bottom sheet for modals and overlays
 */
const BottomSheet = ({
  visible,
  onClose,
  title,
  children,
  height = '50%',
  showCloseButton = true
}) => {
  const [shouldRender, setShouldRender] = useState(visible);

  useEffect(() => {
    if (visible) {
      setShouldRender(true);
      document.body.style.overflow = 'hidden';
    } else {
      const timer = setTimeout(() => {
        setShouldRender(false);
        document.body.style.overflow = 'unset';
      }, 300);
      return () => {
        clearTimeout(timer);
        document.body.style.overflow = 'unset';
      };
    }
  }, [visible]);

  if (!shouldRender) return null;

  return (
    <div 
      className={`fixed inset-0 z-[100] flex flex-col justify-end bg-black/70 transition-opacity duration-300 ${
        visible ? 'opacity-100' : 'opacity-0'
      }`}
      onClick={onClose}
    >
      <div
        className={`bg-white dark:bg-zinc-900 border-t border-gray-200 dark:border-white/10 rounded-t-[32px] transition-all duration-300 ease-out flex flex-col ${
          visible ? 'translate-y-0' : 'translate-y-full'
        }`}
        style={{ maxHeight: height }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className="flex flex-row justify-between items-center p-6 pb-4 border-b border-gray-100 dark:border-white/5">
            {title && <h2 className="text-gray-900 dark:text-white text-2xl font-black">{title}</h2>}
            {showCloseButton && (
              <button
                className="p-1 hover:bg-gray-100 dark:hover:bg-white/5 rounded-full transition-colors"
                onClick={onClose}
              >
                <X size={24} className="text-gray-500 dark:text-zinc-400" />
              </button>
            )}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 pb-10">
          {children}
        </div>
      </div>
    </div>
  );
};

export default BottomSheet;
