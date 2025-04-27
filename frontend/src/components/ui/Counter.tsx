import React, { useState, useEffect } from 'react';

type CounterProps = {
  value: number;
  duration?: number;
  className?: string;
  formatter?: (value: number) => string;
};

export const Counter: React.FC<CounterProps> = ({ 
  value, 
  duration = 1000, 
  className = '',
  formatter = (val) => val.toString() 
}) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let startTime: number | null = null;
    let animationFrameId: number;
    
    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = timestamp - startTime;
      const percentage = Math.min(progress / duration, 1);
      
      setCount(Math.floor(percentage * value));
      
      if (percentage < 1) {
        animationFrameId = requestAnimationFrame(step);
      }
    };
    
    animationFrameId = requestAnimationFrame(step);
    
    return () => cancelAnimationFrame(animationFrameId);
  }, [value, duration]);
  
  return <span className={className}>{formatter(count)}</span>;
};