import React from 'react';
import { Card } from '../ui/Card';
import { AttackOrigin } from '../../types';

type ThreatMapProps = {
  attackOrigins: AttackOrigin[];
};

export const ThreatMap: React.FC<ThreatMapProps> = ({ attackOrigins }) => {
  // For demo purposes, we'll display a simplified representation
  // In a real app, you would use a mapping library like react-simple-maps
  
  // Get the top 5 attack origins for display
  const topAttacks = [...attackOrigins]
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);
  
  const maxCount = Math.max(...attackOrigins.map(origin => origin.count));
  
  return (
    <Card title="Threat Map" subtitle="Attack origin countries">
      <div className="flex justify-center mb-4">
        <div className="text-center text-sm text-slate-500 dark:text-slate-400">
          Interactive map visualization would appear here.
          <div className="mt-2 text-xs">
            Showing attacks from {attackOrigins.length} countries.
          </div>
        </div>
      </div>
      
      <div className="space-y-3 mt-4">
        <h4 className="text-sm font-medium text-slate-900 dark:text-white">Top Attack Sources</h4>
        
        {topAttacks.map((origin) => {
          const percentage = (origin.count / maxCount) * 100;
          
          return (
            <div key={origin.country} className="flex items-center">
              <div className="w-8 flex-shrink-0">
                <span className="text-xs font-medium text-slate-700 dark:text-slate-300">
                  {origin.country}
                </span>
              </div>
              
              <div className="ml-3 flex-1">
                <div className="relative h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                  <div 
                    className="absolute top-0 left-0 h-full bg-red-500 dark:bg-red-600"
                    style={{ width: `${percentage}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="ml-3 w-16 text-right">
                <span className="text-xs font-medium text-slate-700 dark:text-slate-300">
                  {origin.count}
                </span>
              </div>
            </div>
          );
        })}
        
        <div className="text-center mt-4">
          <button className="text-xs text-indigo-600 dark:text-indigo-400 font-medium hover:underline">
            View detailed map
          </button>
        </div>
      </div>
    </Card>
  );
};