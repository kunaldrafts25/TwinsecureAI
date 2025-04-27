import React from 'react';
import { Card } from '../ui/Card';
import { AttackTrend } from '../../types';

type AttackTrendsProps = {
  trends: AttackTrend[];
};

export const AttackTrends: React.FC<AttackTrendsProps> = ({ trends }) => {
  // Get max values to scale the chart properly
  const maxBlocked = Math.max(...trends.map(trend => trend.blockedAttacks));
  const maxHoneypot = Math.max(...trends.map(trend => trend.honeypotHits));
  const maxAnomalies = Math.max(...trends.map(trend => trend.anomalies));
  
  // Format dates for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };
  
  return (
    <Card title="Attack Trends" subtitle="7-day activity overview">
      <div className="h-64 mt-4">
        {/* Chart area */}
        <div className="relative h-full">
          {/* Y-axis labels */}
          <div className="absolute left-0 top-0 bottom-0 w-10 flex flex-col justify-between text-xs text-slate-500 dark:text-slate-400">
            <div>Max</div>
            <div>0</div>
          </div>
          
          {/* Chart visualization */}
          <div className="ml-10 h-full flex items-end">
            {trends.map((trend, index) => (
              <div 
                key={trend.date} 
                className="flex-1 flex flex-col items-center"
                style={{ height: '100%' }}
              >
                {/* Anomalies bar */}
                <div className="relative w-full flex justify-center">
                  <div 
                    className="w-2 bg-purple-500 dark:bg-purple-600 rounded-t-sm"
                    style={{ 
                      height: `${(trend.anomalies / maxAnomalies) * 30}%`,
                      marginTop: 'auto'
                    }}
                  ></div>
                </div>
                
                {/* Honeypot hits bar */}
                <div className="relative w-full flex justify-center">
                  <div 
                    className="w-4 bg-amber-500 dark:bg-amber-600 rounded-t-sm"
                    style={{ 
                      height: `${(trend.honeypotHits / maxHoneypot) * 40}%`,
                      marginTop: 'auto' 
                    }}
                  ></div>
                </div>
                
                {/* Blocked attacks bar */}
                <div className="relative w-full flex justify-center">
                  <div 
                    className="w-6 bg-red-500 dark:bg-red-600 rounded-t-sm"
                    style={{ 
                      height: `${(trend.blockedAttacks / maxBlocked) * 70}%`,
                      marginTop: 'auto'
                    }}
                  ></div>
                </div>
                
                {/* X-axis label */}
                <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  {formatDate(trend.date)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Legend */}
      <div className="flex justify-center mt-4 space-x-6">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-red-500 dark:bg-red-600 rounded-sm"></div>
          <span className="ml-1.5 text-xs text-slate-600 dark:text-slate-300">Blocked Attacks</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-amber-500 dark:bg-amber-600 rounded-sm"></div>
          <span className="ml-1.5 text-xs text-slate-600 dark:text-slate-300">Honeypot Hits</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-purple-500 dark:bg-purple-600 rounded-sm"></div>
          <span className="ml-1.5 text-xs text-slate-600 dark:text-slate-300">Anomalies</span>
        </div>
      </div>
    </Card>
  );
};