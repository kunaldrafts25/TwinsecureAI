import React from 'react';
import { BellRing, Moon, Search, Sun, User } from 'lucide-react';
import { Badge } from '../ui/Badge';

type HeaderProps = {
  title: string;
  alertCount: number;
  darkMode: boolean;
  toggleDarkMode: () => void;
};

export const Header: React.FC<HeaderProps> = ({ 
  title, 
  alertCount, 
  darkMode, 
  toggleDarkMode 
}) => {
  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 sticky top-0 z-10">
      <h1 className="text-xl font-semibold text-slate-900 dark:text-white">
        {title}
      </h1>
      
      <div className="flex-1 max-w-lg mx-auto px-6">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <Search size={18} className="text-slate-400" />
          </div>
          <input
            type="search"
            placeholder="Search threats, alerts, IPs..."
            className="block w-full pl-10 pr-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm dark:text-white dark:placeholder-slate-400"
          />
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        {/* Notifications */}
        <button className="relative p-2 text-slate-500 hover:text-slate-700 rounded-full hover:bg-slate-100 dark:text-slate-400 dark:hover:text-slate-300 dark:hover:bg-slate-800">
          <BellRing size={20} />
          {alertCount > 0 && (
            <Badge 
              variant="critical" 
              className="absolute -top-1 -right-1 px-1.5 py-0.5 min-w-[18px] h-[18px] flex items-center justify-center"
            >
              {alertCount}
            </Badge>
          )}
        </button>
        
        {/* Dark mode toggle */}
        <button 
          onClick={toggleDarkMode}
          className="p-2 text-slate-500 hover:text-slate-700 rounded-full hover:bg-slate-100 dark:text-slate-400 dark:hover:text-slate-300 dark:hover:bg-slate-800"
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
        
        {/* User button */}
        <button className="flex items-center">
          <div className="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
            <User size={16} />
          </div>
        </button>
      </div>
    </header>
  );
};