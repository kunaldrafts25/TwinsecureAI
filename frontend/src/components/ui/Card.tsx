import React from 'react';

type CardProps = {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  footer?: React.ReactNode;
  onClick?: () => void;
};

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  subtitle,
  icon,
  footer,
  onClick,
}) => {
  return (
    <div 
      className={`bg-white dark:bg-slate-800/80 backdrop-blur rounded-lg shadow-md border border-slate-200 dark:border-slate-700/50 h-full transition-all hover:shadow-lg ${
        onClick ? 'cursor-pointer' : ''
      } ${className}`}
      onClick={onClick}
    >
      {(title || icon) && (
        <div className="flex items-center border-b border-slate-200 dark:border-slate-700/50 p-4">
          {icon && <div className="mr-3 text-slate-500 dark:text-slate-400">{icon}</div>}
          <div>
            {title && <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>}
            {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>}
          </div>
        </div>
      )}
      
      <div className="p-4">{children}</div>
      
      {footer && (
        <div className="border-t border-slate-200 dark:border-slate-700/50 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-b-lg">
          {footer}
        </div>
      )}
    </div>
  );
};