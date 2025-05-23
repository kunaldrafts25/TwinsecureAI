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
import { cn } from '../../utils/lib';

interface RiskScoreGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

const RiskScoreGauge: React.FC<RiskScoreGaugeProps> = ({
  score,
  size = 'md',
  showLabel = true,
  className,
}) => {
  // Calculate gauge percentage
  const percentage = Math.min(Math.max(score, 0), 100);
  
  // Determine risk level and color
  const getRiskLevel = () => {
    if (score < 40) return { level: 'Low', color: 'text-severity-low' };
    if (score < 70) return { level: 'Medium', color: 'text-severity-medium' };
    if (score < 90) return { level: 'High', color: 'text-severity-high' };
    return { level: 'Critical', color: 'text-severity-critical' };
  };
  
  const { level, color } = getRiskLevel();
  
  // Sizes
  const sizes = {
    sm: 'w-24 h-12',
    md: 'w-36 h-18',
    lg: 'w-48 h-24',
  };
  
  // Calculate rotation based on score (0-180 degrees)
  const rotation = (percentage / 100) * 180;
  
  return (
    <div className={cn('flex flex-col items-center', className)}>
      <div className={cn('relative', sizes[size])}>
        {/* Gauge background */}
        <div className="absolute h-full w-full overflow-hidden rounded-t-full bg-border">
          <div className="absolute bottom-0 left-0 h-1/2 w-full rounded-t-full bg-card"></div>
        </div>
        
        {/* Gauge indicator */}
        <div 
          className="absolute bottom-0 left-1/2 origin-bottom -translate-x-1/2 transform transition-transform duration-700 ease-out"
          style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
        >
          <div className="h-[calc(100%-8px)] w-1 rounded-full bg-foreground"></div>
          <div className={cn('h-3 w-3 rounded-full', color)}></div>
        </div>
        
        {/* Score display */}
        <div className="absolute bottom-0 left-0 flex h-1/2 w-full flex-col items-center justify-center">
          <span className={cn('text-xl font-bold', color)}>{score}</span>
          {showLabel && <span className="text-xs text-foreground/70">{level} Risk</span>}
        </div>
      </div>
      
      {/* Labels */}
      <div className="mt-1 flex w-full justify-between text-xs text-foreground/50">
        <span>0</span>
        <span>50</span>
        <span>100</span>
      </div>
    </div>
  );
};

export default RiskScoreGauge;