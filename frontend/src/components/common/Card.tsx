import React from 'react';
import { cn } from '../../utils/lib';

interface CardProps {
  className?: string;
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  isLoading?: boolean;
}

const Card: React.FC<CardProps> = ({
  className,
  children,
  title,
  subtitle,
  action,
  isLoading = false,
}) => {
  return (
    <div className={cn('rounded-lg border border-border bg-card p-5 shadow-sm', className)}>
      {(title || action) && (
        <div className="mb-4 flex items-center justify-between">
          <div>
            {title && <h3 className="text-lg font-medium text-card-foreground">{title}</h3>}
            {subtitle && <p className="mt-1 text-sm text-card-foreground/70">{subtitle}</p>}
          </div>
          {action && <div className="ml-auto">{action}</div>}
        </div>
      )}
      
      <div className={cn(isLoading && 'animate-pulse')}>
        {isLoading ? (
          <div className="space-y-3">
            <div className="h-4 w-3/4 rounded bg-border"></div>
            <div className="h-4 w-full rounded bg-border"></div>
            <div className="h-4 w-1/2 rounded bg-border"></div>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
};

export default Card;