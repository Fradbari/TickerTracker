import React, { useState, useRef, useEffect } from 'react';
import { theme } from '../../styles/theme';

interface TooltipProps {
  content: string;
  children: React.ReactNode;
}

export const Tooltip: React.FC<TooltipProps> = ({ content, children }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const wrapperRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isVisible && wrapperRef.current && tooltipRef.current) {
      const rect = wrapperRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      
      let top = rect.bottom + window.scrollY + 8;
      let left = rect.left + window.scrollX;

      // Adjust if it goes outside viewport
      if (left + tooltipRect.width > window.innerWidth) {
        left = Math.max(0, window.innerWidth - tooltipRect.width - 16);
      }
      
      setPosition({ top, left });
    }
  }, [isVisible]);

  return (
    <div 
      className="inline-block"
      ref={wrapperRef}
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div
          ref={tooltipRef}
          style={{
            position: 'absolute',
            top: position.top,
            left: position.left,
            backgroundColor: theme.colors.surface,
            color: theme.colors.text,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.radius.sm,
            padding: '8px 12px',
            fontSize: '12px',
            fontFamily: theme.font.body,
            maxWidth: '300px',
            zIndex: 9999,
            pointerEvents: 'none',
            boxShadow: theme.shadow.dropdown,
          }}
        >
          {content}
        </div>
      )}
    </div>
  );
};
