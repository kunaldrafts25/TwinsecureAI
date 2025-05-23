/*
 * TwinSecure - Advanced Cybersecurity Platform
 * Copyright © 2024 TwinSecure. All rights reserved.
 * 
 * This file is part of TwinSecure, a proprietary cybersecurity platform.
 * Unauthorized copying, distribution, modification, or use of this software
 * is strictly prohibited without explicit written permission.
 * 
 * For licensing inquiries: kunalsingh2514@gmail.com
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Bell, 
  LogOut, 
  Moon, 
  MoreVertical, 
  Settings, 
  Sun, 
  User,
  Shield,
} from 'lucide-react';
import { useAuthStore } from '../../features/auth/store/authStore';
import { useThemeStore } from '../../store/themeStore';
import { getInitials } from '../../utils/lib';
import Button from '../common/Button';

const Header: React.FC = () => {
  const { user, logout } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const handleLogout = async () => {
    await logout();
  };
  
  const toggleUserMenu = () => {
    setShowUserMenu(!showUserMenu);
  };
  
  return (
    <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-border bg-card/80 px-6 backdrop-blur-sm">
      <div className="md:hidden">
        <Link to="/" className="flex items-center gap-2">
          <Shield className="h-6 w-6 text-primary" />
          <span className="text-lg font-bold text-card-foreground">TwinSecure</span>
        </Link>
      </div>
      
      <div className="flex-1"></div>
      
      <div className="flex items-center gap-2">
        <button
          onClick={toggleTheme}
          className="flex h-9 w-9 items-center justify-center rounded-full text-card-foreground/70 hover:bg-card-foreground/5 hover:text-card-foreground"
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        
        <button
          className="flex h-9 w-9 items-center justify-center rounded-full text-card-foreground/70 hover:bg-card-foreground/5 hover:text-card-foreground"
          aria-label="Notifications"
        >
          <Bell size={18} />
        </button>
        
        <div className="relative">
          <button
            onClick={toggleUserMenu}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary hover:bg-primary/20"
            aria-label="User menu"
          >
            {user ? getInitials(user.full_name) : <User size={16} />}
          </button>
          
          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-48 origin-top-right rounded-md border border-border bg-card shadow-lg ring-1 ring-black ring-opacity-5">
              <div className="p-2">
                {user && (
                  <div className="border-b border-border px-4 py-2">
                    <p className="font-medium text-card-foreground">{user.full_name}</p>
                    <p className="text-xs text-card-foreground/70">{user.email}</p>
                  </div>
                )}
                
                <div className="py-1">
                  <Link
                    to="/profile"
                    className="flex items-center gap-2 rounded-md px-4 py-2 text-sm text-card-foreground hover:bg-card-foreground/5"
                    onClick={() => setShowUserMenu(false)}
                  >
                    <User size={16} />
                    Profile
                  </Link>
                  
                  <Link
                    to="/settings"
                    className="flex items-center gap-2 rounded-md px-4 py-2 text-sm text-card-foreground hover:bg-card-foreground/5"
                    onClick={() => setShowUserMenu(false)}
                  >
                    <Settings size={16} />
                    Settings
                  </Link>
                  
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2 rounded-md px-4 py-2 text-sm text-error hover:bg-card-foreground/5"
                  >
                    <LogOut size={16} />
                    Sign out
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;