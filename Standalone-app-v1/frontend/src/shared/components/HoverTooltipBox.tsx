import React, { useState, useRef, useEffect } from 'react'

interface HoverTooltipBoxProps {
  children: React.ReactNode;
  description: React.ReactNode;
  className?: string;
  tooltipClassName?: string;
  delay?: number;
}

export function HoverTooltipBox({ children, description, className = '', tooltipClassName = '', delay = 3000 }: HoverTooltipBoxProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const handleMouseEnter = () => {
    if (!description) return;
    timerRef.current = setTimeout(() => {
      setShowTooltip(true);
    }, delay);
  };

  const handleMouseLeave = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    setShowTooltip(false);
  };

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  return (
    <div 
      className={`relative ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      
      {/* Tooltip */}
      {showTooltip && description && (
        <div className={`absolute z-[100] left-1/2 -translate-x-1/2 w-64 p-4 bg-slate-800 text-white text-xs rounded-xl shadow-2xl text-left pointer-events-none animate-in fade-in zoom-in duration-200 ${tooltipClassName}`}>
          <div className="leading-relaxed whitespace-pre-wrap">{description}</div>
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-8 border-transparent border-t-slate-800" />
        </div>
      )}
    </div>
  )
}
