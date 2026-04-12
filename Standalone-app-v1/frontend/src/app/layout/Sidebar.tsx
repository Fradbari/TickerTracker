import { NavLink } from "react-router-dom";
import { LayoutDashboard, Wallet, BrainCircuit, Settings } from "lucide-react";
import { ThemeToggle } from "../../shared/components/ThemeToggle";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Portfolio", href: "/portfolio", icon: Wallet },
  { label: "AI Analysis", href: "/analysis", icon: BrainCircuit },
  { label: "Admin", href: "/admin", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-[var(--card)] border-r border-[var(--border)] hidden md:flex flex-col h-screen fixed inset-y-0 left-0 z-50">
      <div className="p-6 flex items-center justify-between">
        <h1 className="text-xl font-bold text-[var(--foreground)] truncate">
          Ticker Tracker
        </h1>
        <ThemeToggle />
      </div>

      <nav className="flex-1 px-4 space-y-2 mt-4 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? "bg-[var(--accent)] text-white font-medium"
                  : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 dark:text-slate-400"
              }`
            }
          >
            <item.icon size={20} />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
