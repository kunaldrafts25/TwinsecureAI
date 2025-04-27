import React from 'react';

type BadgeProps = {
  variant: 'low' | 'medium' | 'high' | 'critical' | 'neutral';
  children: React.ReactNode;
  className?: string;
};

const variantClasses = {
  low: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  medium: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
  high: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
  critical: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  neutral: 'bg-slate-100 text-slate-800 dark:bg-slate-800/50 dark:text-slate-300',
};

export const Badge: React.FC<BadgeProps> = ({ variant, children, className = '' }) => {
  return (
    <span 
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variantClasses[variant]} ${className}`}
    >
      {children}
    </span>
  );
};