import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Map, Filter, Globe, AlertTriangle } from 'lucide-react';
import { attackOrigins } from '../data/mockData';
import { AttackOrigin } from '../types';

export const ThreatMapPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [threatLevel, setThreatLevel] = useState('all');
  
  const totalAttacks = attackOrigins.reduce((sum, origin) => sum + origin.count, 0);
  const highRiskCountries = attackOrigins.filter(origin => origin.count > 500).length;
  
  return (
    <div className="p-6 space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Globe size={24} className="text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Total Attacks</h3>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{totalAttacks.toLocaleString()}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
              <Map size={24} className="text-amber-600 dark:text-amber-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Active Countries</h3>
              <p className="text-3xl font-bold text-amber-600 dark:text-amber-400">{attackOrigins.length}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <AlertTriangle size={24} className="text-red-600 dark:text-red-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">High Risk Countries</h3>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">{highRiskCountries}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="space-x-2">
          {['1h', '24h', '7d', '30d'].map(range => (
            <Button
              key={range}
              variant={timeRange === range ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setTimeRange(range)}
            >
              {range}
            </Button>
          ))}
        </div>
        
        <div className="border-l border-slate-200 dark:border-slate-700 h-6 mx-2" />
        
        <div className="space-x-2">
          {['all', 'high', 'medium', 'low'].map(level => (
            <Button
              key={level}
              variant={threatLevel === level ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setThreatLevel(level)}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Main Map Card */}
      <Card title="Global Threat Map" subtitle="Real-time attack visualization">
        <div className="h-[500px] bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center">
          <p className="text-slate-500 dark:text-slate-400">Interactive map visualization would be rendered here</p>
        </div>
      </Card>

      {/* Attack Origins Table */}
      <Card title="Top Attack Origins" subtitle="Detailed country-wise breakdown">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700/50">
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500 dark:text-slate-400">Country</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500 dark:text-slate-400">Attacks</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500 dark:text-slate-400">Trend</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500 dark:text-slate-400">Risk Level</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-500 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {attackOrigins
                .sort((a, b) => b.count - a.count)
                .map(origin => (
                  <tr key={origin.country} className="border-b border-slate-200 dark:border-slate-700/50">
                    <td className="py-4 px-4">
                      <div className="font-medium text-slate-900 dark:text-white">{origin.country}</div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="font-medium">{origin.count.toLocaleString()}</div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="w-24 h-2 bg-slate-100 dark:bg-slate-700 rounded-full">
                        <div 
                          className="h-full bg-blue-500 rounded-full"
                          style={{ width: `${(origin.count / totalAttacks) * 100}%` }}
                        ></div>
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <Badge 
                        variant={origin.count > 500 ? 'critical' : origin.count > 200 ? 'high' : 'medium'}
                      >
                        {origin.count > 500 ? 'High' : origin.count > 200 ? 'Medium' : 'Low'}
                      </Badge>
                    </td>
                    <td className="py-4 px-4 text-right">
                      <Button variant="ghost" size="sm">Details</Button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};