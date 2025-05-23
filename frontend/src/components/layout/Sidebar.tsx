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

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  BarChart,
  Bell,
  Boxes,
  FileBarChart,
  Home,
  Settings,
  Shield,
  UserCircle,
} from 'lucide-react';
import { cn } from '../../utils/lib';
import { useAuthStore } from '../../features/auth/store/authStore';
import { UserRole } from '../../types';

interface SidebarItem {
  label: string;
  icon: React.ReactNode;
  path: string;
  roles: string[]; // Changed to string[] to accommodate both backend and frontend roles
}

// Map backend roles to frontend roles
const mapBackendRole = (role: string): string[] => {
  // Convert role to lowercase for case-insensitive comparison
  const lowerRole = role.toLowerCase();

  switch (lowerRole) {
    case 'admin':
      return ['sme_admin', 'superuser'];
    case 'analyst':
      return ['sme_user', 'mssp_user'];
    case 'viewer':
      return ['sme_user'];
    case 'api_user':
      return ['api_user'];
    default:
      // For any unknown role, return it as is
      return [lowerRole];
  }
};

const sidebarItems: SidebarItem[] = [
  {
    label: 'Dashboard',
    icon: <Home size={18} />,
    path: '/dashboard',
    roles: ['sme_admin', 'sme_user', 'superuser', 'admin', 'analyst', 'viewer'],
  },
  {
    label: 'MSSP Dashboard',
    icon: <Boxes size={18} />,
    path: '/mssp',
    roles: ['mssp_user', 'superuser', 'admin', 'analyst'],
  },
  {
    label: 'Alerts',
    icon: <Bell size={18} />,
    path: '/alerts',
    roles: ['sme_admin', 'sme_user', 'mssp_user', 'superuser', 'admin', 'analyst', 'viewer'],
  },
  {
    label: 'Digital Twin',
    icon: <Shield size={18} />,
    path: '/twin',
    roles: ['sme_admin', 'sme_user', 'mssp_user', 'superuser', 'admin', 'analyst', 'viewer'],
  },
  {
    label: 'Reports',
    icon: <FileBarChart size={18} />,
    path: '/reports',
    roles: ['sme_admin', 'sme_user', 'mssp_user', 'superuser', 'admin', 'analyst', 'viewer'],
  },
  {
    label: 'Analytics',
    icon: <BarChart size={18} />,
    path: '/analytics',
    roles: ['sme_admin', 'mssp_user', 'superuser', 'admin', 'analyst'],
  },
  {
    label: 'Profile',
    icon: <UserCircle size={18} />,
    path: '/profile',
    roles: ['sme_admin', 'sme_user', 'mssp_user', 'superuser', 'admin', 'analyst', 'viewer', 'api_user'],
  },
  {
    label: 'Settings',
    icon: <Settings size={18} />,
    path: '/settings',
    roles: ['sme_admin', 'superuser', 'admin'],
  },
];

const Sidebar: React.FC = () => {
  const location = useLocation();
  const { user } = useAuthStore();

  // Check if user role exists in item roles directly or via mapping
  const filteredItems = sidebarItems.filter((item) => {
    if (!user || !user.role) return false;

    // Convert user role to lowercase for case-insensitive comparison
    const userRole = user.role.toLowerCase();

    // Check if the item roles include the user role directly
    if (item.roles.includes(userRole)) return true;

    // Check if the mapped roles for the user role are included in item roles
    const mappedRoles = mapBackendRole(userRole);
    return mappedRoles.some(role => item.roles.includes(role));
  });

  return (
    <div className="h-full w-64 border-r border-border bg-card">
      <div className="flex h-16 items-center border-b border-border px-6">
        <Link to="/" className="flex items-center gap-2">
          <Shield className="h-6 w-6 text-primary" />
          <span className="text-lg font-bold text-card-foreground">TwinSecure AI</span>
        </Link>
      </div>

      <nav className="p-4">
        <ul className="space-y-1">
          {filteredItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={cn(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
                  location.pathname === item.path
                    ? 'bg-primary/10 text-primary'
                    : 'text-card-foreground/70 hover:bg-card-foreground/5 hover:text-card-foreground'
                )}
              >
                {item.icon}
                <span>{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;
