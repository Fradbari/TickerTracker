import React from "react";

interface KpiCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  isLoading?: boolean;
}

export function KpiCard({ title, value, icon, trend, isLoading }: KpiCardProps) {
  if (isLoading) {
    return (
      <div className="p-6 rounded-xl bg-[var(--card)] border border-[var(--border)] animate-pulse">
        <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-1/3 mb-4"></div>
        <div className="h-8 bg-slate-300 dark:bg-slate-700 rounded w-1/2"></div>
      </div>
    );
  }

  return (
    <div className="p-6 rounded-xl bg-[var(--card)] text-[var(--card-foreground)] border border-[var(--border)] shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400">
          {title}
        </h3>
        {icon && <div className="text-[var(--accent)]">{icon}</div>}
      </div>
      
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold">{value}</span>
        {trend && (
          <span
            className={`text-sm font-medium ${
              trend.isPositive ? "text-[var(--success)]" : "text-[var(--danger)]"
            }`}
          >
            {trend.isPositive ? "+" : ""}{trend.value}
          </span>
        )}
      </div>
    </div>
  );
}
