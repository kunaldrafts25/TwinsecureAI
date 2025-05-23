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
import { Calendar } from 'lucide-react';
import { DashboardFilters } from '../../types';

interface TimeRangeSelectorProps {
  currentRange: DashboardFilters['timeRange'];
  onChange: (range: DashboardFilters['timeRange']) => void;
  className?: string;
}

const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({
  currentRange,
  onChange,
  className = '',
}) => {
  const timeRanges: { value: DashboardFilters['timeRange']; label: string }[] = [
    { value: '24h', label: 'Last 24 hours' },
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 90 days' },
    { value: 'custom', label: 'Custom range' },
  ];

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <Calendar size={16} className="text-muted-foreground" />
      <div className="flex rounded-md shadow-sm">
        {timeRanges.map((range) => (
          <button
            key={range.value}
            type="button"
            onClick={() => onChange(range.value)}
            className={`px-3 py-1.5 text-sm font-medium ${
              currentRange === range.value
                ? 'bg-primary text-primary-foreground'
                : 'bg-background text-foreground hover:bg-muted'
            } ${
              range.value === timeRanges[0].value
                ? 'rounded-l-md'
                : range.value === timeRanges[timeRanges.length - 1].value
                ? 'rounded-r-md'
                : ''
            }`}
          >
            {range.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default TimeRangeSelector;
