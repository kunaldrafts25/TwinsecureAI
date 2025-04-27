import React from 'react';
import { 
  ShieldAlert, 
  LineChart, 
  Map, 
  Radar, 
  Bell, 
  FileText, 
  Settings, 
  HelpCircle, 
  LogOut, 
  Home,
  Shield
} from 'lucide-react';

type SidebarItemProps = {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  onClick?: () => void;
};

const SidebarItem: React.FC<SidebarItemProps> = ({ icon, label, active = false, onClick }) => {
  return (
    <li>
      <button
        onClick={onClick}
        className={`flex items-center w-full px-3 py-2.5 rounded-lg text-left transition-all ${
          active 
            ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300' 
            : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800/60'
        }`}
      >
        <span className="w-6 h-6">{icon}</span>
        <span className="ml-3 font-medium">{label}</span>
      </button>
    </li>
  );
};

type SidebarProps = {
  activePage: string;
  onPageChange: (page: string) => void;
};

export const Sidebar: React.FC<SidebarProps> = ({ activePage, onPageChange }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <Home size={18} /> },
    { id: 'alerts', label: 'Alerts', icon: <Bell size={18} /> },
    { id: 'threats', label: 'Threat Map', icon: <Map size={18} /> },
    { id: 'honeypot', label: 'Honeypot', icon: <ShieldAlert size={18} /> },
    { id: 'analytics', label: 'Analytics', icon: <LineChart size={18} /> },
    { id: 'anomalies', label: 'Anomalies', icon: <Radar size={18} /> },
    { id: 'reports', label: 'Reports', icon: <FileText size={18} /> },
  ];

  const secondaryItems = [
    { id: 'settings', label: 'Settings', icon: <Settings size={18} /> },
    { id: 'help', label: 'Help & Support', icon: <HelpCircle size={18} /> },
  ];
  
  return (
    <div className="h-screen flex flex-col bg-white border-r border-slate-200 dark:bg-slate-900 dark:border-slate-800 w-56 fixed top-0 left-0">
      <div className="flex items-center px-4 py-6">
        <div className="p-1.5 bg-indigo-600 rounded text-white">
          <Shield size={22} />
        </div>
        <h1 className="ml-2 text-xl font-bold text-slate-900 dark:text-white">TwinSecure AI</h1>
      </div>
      
      <nav className="flex-1 px-3 py-2 overflow-y-auto">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <SidebarItem
              key={item.id}
              icon={item.icon}
              label={item.label}
              active={activePage === item.id}
              onClick={() => onPageChange(item.id)}
            />
          ))}
        </ul>
        
        <div className="my-4 border-t border-slate-200 dark:border-slate-700"></div>
        
        <ul className="space-y-1">
          {secondaryItems.map((item) => (
            <SidebarItem
              key={item.id}
              icon={item.icon}
              label={item.label}
              active={activePage === item.id}
              onClick={() => onPageChange(item.id)}
            />
          ))}
        </ul>
      </nav>
      
      <div className="p-4 border-t border-slate-200 dark:border-slate-700">
        <button className="flex items-center w-full px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg dark:text-red-400 dark:hover:bg-red-900/20">
          <LogOut size={18} />
          <span className="ml-3">Log out</span>
        </button>
      </div>
    </div>
  );
};