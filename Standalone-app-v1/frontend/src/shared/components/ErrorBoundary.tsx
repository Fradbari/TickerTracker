import React, { Component, ErrorInfo, ReactNode } from "react";
import { TriangleAlert } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8 m-4 bg-[var(--card)] border border-[var(--danger)] rounded-xl shadow-lg text-center">
          <TriangleAlert className="text-[var(--danger)] mb-4" size={48} />
          <h2 className="text-2xl font-bold text-[var(--foreground)] mb-2">
            Qualcosa è andato storto
          </h2>
          <p className="text-slate-500 dark:text-slate-400 mb-6 max-w-md">
            {this.state.error?.message || "Si è verificato un errore critico nel rendering di questo componente."}
          </p>
          <button
            className="px-6 py-2 bg-[var(--accent)] hover:opacity-90 text-white rounded-lg transition-opacity"
            onClick={() => window.location.reload()}
          >
            Ricarica la pagina
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
