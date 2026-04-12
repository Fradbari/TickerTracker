import React, { useState, useRef, useEffect } from "react";

interface KpiCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  isLoading?: boolean;
  description?: string;
}

export function KpiCard({ title, value, icon, trend, isLoading, description }: KpiCardProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const handleMouseEnter = () => {
    if (!description) return;
    timerRef.current = setTimeout(() => {
      setShowTooltip(true);
    }, 3000);
  };

  const handleMouseLeave = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
    setShowTooltip(false);
  };

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  if (isLoading) {
    return (
      <div className="p-6 rounded-xl bg-[var(--card)] border border-[var(--border)] animate-pulse">
        <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-1/3 mb-4"></div>
        <div className="h-8 bg-slate-300 dark:bg-slate-700 rounded w-1/2"></div>
      </div>
    );
  }

  return (
    <div 
      className="relative p-6 rounded-xl bg-[var(--card)] text-[var(--card-foreground)] border border-[var(--border)] shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 group cursor-default"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400 min-w-0 pr-2 truncate">
          {title}
        </h3>
        {icon && <div className="text-[var(--accent)] flex-shrink-0">{icon}</div>}
      </div>
      
      <div className="flex flex-wrap items-baseline gap-2">
        <span className="text-2xl sm:text-3xl font-bold max-w-full break-words">{value}</span>
        {trend && (
          <span
            className={`text-sm font-medium whitespace-nowrap ${
              trend.isPositive ? "text-[var(--success)]" : "text-[var(--danger)]"
            }`}
          >
            {trend.isPositive ? "+" : ""}{trend.value}
          </span>
        )}
      </div>

      {/* Tooltip */}
      {showTooltip && description && (
        <div className="absolute z-50 bottom-[calc(100%+0.5rem)] left-1/2 -translate-x-1/2 w-48 sm:w-64 p-3 bg-slate-800 text-white text-xs rounded-lg shadow-xl text-center pointer-events-none animate-in fade-in zoom-in duration-200">
          <p>{description}</p>
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-800" />
        </div>
      )}
    </div>
  );
}
