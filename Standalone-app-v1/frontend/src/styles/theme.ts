export const theme = {
  colors: {
    textInverse: '#ffffff',
    bg: '#0d1117',
    surface: '#161b22',
    border: '#21262d',
    borderSubtle: '#30363d',
    text: '#e6edf3',
    textMuted: '#8b949e',
    textFaint: '#484f58',
    accent: '#1f6feb',
    success: '#238636',          // TARGET HIT / P&L positivo
    danger: '#da3633',           // STOP HIT / P&L negativo
    warning: '#d29922',          // FETCHING / in attesa
    info: '#1f6feb',             // ACTIVE
    expired: '#484f58',          // EXPIRED
  },
  estimateStatus: {
    OPEN:         '#1f6feb',
    CLOSED_WIN:   '#238636',
    CLOSED_LOSS:  '#da3633',
    FETCHING:     '#d29922',
    EXPIRED:      '#484f58',
    ERROR:        '#f85149',
  },
  radius: { sm: '4px', md: '6px', lg: '8px' },
  shadow: { card: '0 1px 3px rgba(0,0,0,0.4)', dropdown: '0 8px 24px rgba(0,0,0,0.5)' },
  font: { 
      body: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", 
      mono: "'SF Mono', 'Fira Code', monospace" 
  }
} as const;
