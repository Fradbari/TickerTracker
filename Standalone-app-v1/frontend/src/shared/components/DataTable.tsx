import React, { ReactNode } from "react";
import { Skeleton } from "./Skeleton";

export interface ColumnDef<T> {
  header: string | ReactNode;
  accessorKey?: keyof T;
  cell?: (item: T) => ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  isLoading?: boolean;
  emptyMessage?: string;
  onRowClick?: (item: T) => void;
}

export function DataTable<T>({
  data,
  columns,
  isLoading,
  emptyMessage = "Nessun dato trovato",
  onRowClick,
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="bg-[var(--card)] rounded-xl overflow-hidden border border-[var(--border)] shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-slate-50 dark:bg-slate-800/50 uppercase text-slate-500 dark:text-slate-400">
              <tr>
                {columns.map((col, i) => (
                  <th key={i} className={`px-6 py-4 font-medium ${col.className || ""}`}>
                    {col.header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: 5 }).map((_, rowIndex) => (
                <tr key={rowIndex} className="border-b border-[var(--border)] last:border-0 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                  {columns.map((col, colIndex) => (
                    <td key={colIndex} className={`px-6 py-4 ${col.className || ""}`}>
                      <Skeleton className="h-4 w-full max-w-[80%]" />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  if (!data.length) {
    return (
      <div className="bg-[var(--card)] rounded-xl border border-[var(--border)] shadow-sm p-12 flex flex-col items-center justify-center text-slate-500 dark:text-slate-400">
        <p>{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="bg-[var(--card)] rounded-xl overflow-hidden border border-[var(--border)] shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-slate-50 dark:bg-slate-800/50 uppercase text-slate-500 dark:text-slate-400 border-b border-[var(--border)]">
            <tr>
              {columns.map((col, i) => (
                <th key={i} className={`px-6 py-4 font-medium tracking-wider ${col.className || ""}`}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((item, rowIndex) => (
              <tr
                key={rowIndex}
                onClick={() => onRowClick?.(item)}
                className={`border-b border-[var(--border)] last:border-0 transition-colors ${
                  onRowClick ? "cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/50" : "hover:bg-slate-50/30 dark:hover:bg-slate-800/20"
                }`}
              >
                {columns.map((col, colIndex) => (
                  <td key={colIndex} className={`px-6 py-4 text-[var(--foreground)] ${col.className || ""}`}>
                    {col.cell ? col.cell(item) : col.accessorKey ? String(item[col.accessorKey] ?? "-") : null}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
