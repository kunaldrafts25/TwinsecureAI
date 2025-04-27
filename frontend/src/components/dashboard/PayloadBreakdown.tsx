import React from 'react';
import { Card } from '../ui/Card';
import { PayloadType } from '../../types';

type PayloadBreakdownProps = {
  payloadTypes: PayloadType[];
};

export const PayloadBreakdown: React.FC<PayloadBreakdownProps> = ({ payloadTypes }) => {
  return (
    <Card title="Attack Payloads" subtitle="Distribution by type">
      <div className="mt-2 space-y-4">
        {payloadTypes.map((payload) => (
          <div key={payload.type}>
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                {payload.type}
              </span>
              <span className="text-sm text-slate-500 dark:text-slate-400">
                {payload.percentage.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
              <div 
                className="bg-indigo-600 dark:bg-indigo-500 h-2 rounded-full" 
                style={{ width: `${payload.percentage}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};