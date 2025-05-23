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
import { severityToColor, statusToColor } from '../../utils/lib';

interface StatusIndicatorProps {
  type: 'severity' | 'status';
  value: string;
  showText?: boolean;
  className?: string;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  type,
  value,
  showText = true,
  className,
}) => {
  const getColorClass = () => {
    if (type === 'severity') {
      return severityToColor(value);
    } else {
      return statusToColor(value);
    }
  };

  const label = value.replace('_', ' ');

  return (
    <div className={cn('inline-flex items-center gap-1.5', className)}>
      <span className={cn('h-2 w-2 rounded-full', getColorClass())}></span>
      {showText && <span className="text-xs font-medium capitalize">{label}</span>}
    </div>
  );
};

export default StatusIndicator;