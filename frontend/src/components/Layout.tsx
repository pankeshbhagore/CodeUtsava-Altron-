import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Search, 
  GitBranch, 
  Lightbulb, 
  FlaskConical, 
  ShieldCheck, 
  Activity, 
  History,
  Sun,
  Moon,
  Database
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const navItems = [
  { path: '/overview', label: 'Overview', icon: LayoutDashboard },
  { path: '/query-analyzer', label: 'Query Analyzer', icon: Search },
  { path: '/execution-plan', label: 'Execution Plan', icon: GitBranch },
  { path: '/recommendations', label: 'AI Recommendations', icon: Lightbulb },
  { path: '/simulation-lab', label: 'Simulation Lab', icon: FlaskConical },
  { path: '/privacy-center', label: 'Privacy Center', icon: ShieldCheck },
  { path: '/workload-drift', label: 'Workload Drift', icon: Activity },
  { path: '/audit-log', label: 'Audit Log', icon: History },
];

const Layout: React.FC<LayoutProps> = ({ children, darkMode, toggleDarkMode }) => {
  const location = useLocation();

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-50">
      {/* Sidebar */}
      <aside className="w-64 flex flex-col border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
        <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800">
          <Database className="w-6 h-6 text-blue-600 dark:text-blue-500 mr-2" />
          <span className="font-bold text-lg tracking-tight">PrivDB Optimizer</span>
        </div>
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path);
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400'
                    : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                }`}
              >
                <Icon className={`w-5 h-5 mr-3 ${isActive ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400 dark:text-slate-500'}`} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-slate-200 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Theme</span>
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Toggle dark mode"
            >
              {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="h-16 flex items-center justify-between px-8 border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-950/50 backdrop-blur-sm">
          <h1 className="text-xl font-semibold">
            {navItems.find((i) => location.pathname.startsWith(i.path))?.label || 'Dashboard'}
          </h1>
          <div className="flex items-center space-x-4">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-500 flex items-center justify-center text-white font-semibold shadow-sm">
              AD
            </div>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Layout;
