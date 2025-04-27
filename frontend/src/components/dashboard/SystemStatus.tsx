import React from 'react';
import { Card } from '../ui/Card';
import { SystemMetric } from '../../types';
import { CpuIcon, HardHat as Hard, Database } from 'lucide-react';

type SystemStatusProps = {
  metrics: SystemMetric[];
};

export const SystemStatus: React.FC<SystemStatusProps> = ({ metrics }) => {
  // Get the most recent metrics
  const latestMetric = metrics[metrics.length - 1];
  
  const getStatusClass = (value: number, thresholds: { warning: number; critical: number }) => {
    if (value >= thresholds.critical) {
      return 'text-red-500 dark:text-red-400';
    }
    if (value >= thresholds.warning) {
      return 'text-amber-500 dark:text-amber-400';
    }
    return 'text-green-500 dark:text-green-400';
  };
  
  const cpuStatus = getStatusClass(latestMetric.cpu, { warning: 70, critical: 90 });
  const memoryStatus = getStatusClass(latestMetric.memory, { warning: 80, critical: 95 });
  const errorStatus = getStatusClass(latestMetric.errorRate, { warning: 1, critical: 3 });
  
  return (
    <Card title="System Status" subtitle="Current infrastructure health">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2">
        {/* CPU Usage */}
        <div className="flex items-center">
          <div className="p-2 rounded-full bg-slate-100 dark:bg-slate-800">
            <CpuIcon size={18} className="text-slate-600 dark:text-slate-400" />
          </div>
          <div className="ml-3">
            <div className="text-sm text-slate-500 dark:text-slate-400">CPU</div>
            <div className={`text-lg font-semibold ${cpuStatus}`}>
              {latestMetric.cpu}%
            </div>
          </div>
        </div>
        
        {/* Memory Usage */}
        <div className="flex items-center">
          <div className="p-2 rounded-full bg-slate-100 dark:bg-slate-800">
            <Hard size={18} className="text-slate-600 dark:text-slate-400" />
          </div>
          <div className="ml-3">
            <div className="text-sm text-slate-500 dark:text-slate-400">Memory</div>
            <div className={`text-lg font-semibold ${memoryStatus}`}>
              {latestMetric.memory}%
            </div>
          </div>
        </div>
        
        {/* Error Rate */}
        <div className="flex items-center">
          <div className="p-2 rounded-full bg-slate-100 dark:bg-slate-800">
            <Database size={18} className="text-slate-600 dark:text-slate-400" />
          </div>
          <div className="ml-3">
            <div className="text-sm text-slate-500 dark:text-slate-400">Error Rate</div>
            <div className={`text-lg font-semibold ${errorStatus}`}>
              {latestMetric.errorRate.toFixed(2)}%
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-4">
        <div className="text-xs text-slate-500 dark:text-slate-400">
          Request Rate: <strong>{latestMetric.requests}/min</strong>
        </div>
        <div className="mt-2 h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-green-500 dark:bg-green-600"
            style={{ width: `${Math.min(latestMetric.requests / 10, 100)}%` }}
          ></div>
        </div>
      </div>
    </Card>
  );
};