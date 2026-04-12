import React, { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'

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
  const triggerRef = useRef<HTMLDivElement>(null);
  const [coords, setCoords] = useState({ top: 0, left: 0, width: 0, height: 0 });

  const handleMouseEnter = () => {
    if (!description) return;
    timerRef.current = setTimeout(() => {
      if (triggerRef.current) {
        const rect = triggerRef.current.getBoundingClientRect();
        setCoords({
          top: rect.top,
          left: rect.left,
          width: rect.width,
          height: rect.height,
        });
      }
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

  const getPositionStyles = (): React.CSSProperties => {
    const isBottom = tooltipClassName.includes('-bottom') || tooltipClassName.includes('top-full');

    const result: React.CSSProperties = {
      position: 'fixed',
      left: coords.left + coords.width / 2,
      transform: 'translateX(-50%)',
      zIndex: 999999, // Forza l'overlay massimo (davanti al modal overlay e al body)
      pointerEvents: 'none'
    };

    if (isBottom) {
      result.top = coords.top + coords.height + 8; // Spazio di 8px sotto
    } else {
      result.top = coords.top - 8; // Spazio di 8px sopra
      result.transform = 'translate(-50%, -100%)'; 
    }

    return result;
  };

  return (
    <div 
      ref={triggerRef}
      className={`relative ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      
      {/* Tooltip Portal per scavalcare l'overflow-hidden */}
      {showTooltip && description && typeof document !== 'undefined' && createPortal(
        <div 
          style={getPositionStyles()}
          className={`w-[320px] max-w-[90vw] p-4 bg-slate-800 text-white text-xs rounded-xl shadow-2xl text-left pointer-events-none animate-in fade-in zoom-in duration-200`}
        >
          <div className="leading-relaxed whitespace-pre-wrap">{description}</div>
          <div className={`absolute left-1/2 -translate-x-1/2 border-8 border-transparent ${
            tooltipClassName.includes('-bottom') || tooltipClassName.includes('top-full')
              ? 'bottom-full border-b-slate-800' 
              : 'top-full border-t-slate-800'
          }`} />
        </div>,
        document.body
      )}
    </div>
  )
}
