import React from 'react';
import { Card } from '../ui/Card';
import { Counter } from '../ui/Counter';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

type StatCardProps = {
  title: string;
  value: number;
  icon: React.ReactNode;
  change?: number;
  changeText?: string;
  formatter?: (value: number) => string;
  description?: string;
  className?: string;
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  change,
  changeText,
  formatter = (val) => val.toString(),
  description,
  className = '',
}) => {
  const isPositiveChange = change && change > 0;
  
  return (
    <Card className={className}>
      <div className="flex items-center">
        <div className="p-3 rounded-lg bg-slate-100 dark:bg-slate-800">
          {icon}
        </div>
        <div className="ml-4">
          <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400">
            {title}
          </h3>
          <div className="mt-1 flex items-baseline">
            <div className="text-2xl font-semibold text-slate-900 dark:text-white">
              <Counter value={value} formatter={formatter} />
            </div>
            
            {change !== undefined && (
              <span 
                className={`ml-2 text-sm font-medium flex items-center
                  ${isPositiveChange ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}
              >
                {isPositiveChange ? (
                  <ArrowUpRight size={16} className="mr-0.5" />
                ) : (
                  <ArrowDownRight size={16} className="mr-0.5" />
                )}
                {Math.abs(change)}%
              </span>
            )}
          </div>
          
          {(description || changeText) && (
            <div className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {changeText || description}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};