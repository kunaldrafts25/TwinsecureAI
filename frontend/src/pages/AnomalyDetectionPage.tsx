import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Brain, AlertTriangle, Activity, Zap } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { systemMetrics } from '../data/mockData';

export const AnomalyDetectionPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [metricType, setMetricType] = useState('all');

  // Calculate anomaly stats
  const totalAnomalies = 47; // This would come from your anomaly detection system
  const criticalAnomalies = 12;
  const falsePositives = 8;
  
  return (
    <div className="p-6 space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
              <Brain size={24} className="text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Total Anomalies</h3>
              <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">{totalAnomalies}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <AlertTriangle size={24} className="text-red-600 dark:text-red-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Critical</h3>
              <p className="text-3xl font-bold text-red-600 dark:text-red-400">{criticalAnomalies}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-amber-100 dark:bg-amber-900/30 rounded-lg">
              <Activity size={24} className="text-amber-600 dark:text-amber-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">False Positives</h3>
              <p className="text-3xl font-bold text-amber-600 dark:text-amber-400">{falsePositives}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <Zap size={24} className="text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Detection Rate</h3>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">98.2%</p>
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
          {['all', 'network', 'system', 'user'].map(type => (
            <Button
              key={type}
              variant={metricType === type ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setMetricType(type)}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="System Metrics" subtitle="Real-time performance monitoring">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={systemMetrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()} 
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString()}
                  contentStyle={{
                    backgroundColor: 'rgb(15 23 42)',
                    border: 'none',
                    borderRadius: '0.5rem',
                    padding: '1rem',
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="cpu" 
                  stroke="#8b5cf6" 
                  name="CPU Usage"
                />
                <Line 
                  type="monotone" 
                  dataKey="memory" 
                  stroke="#3b82f6" 
                  name="Memory Usage"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Anomaly Distribution" subtitle="By type and severity">
          <div className="space-y-4">
            {[
              { type: 'Network Traffic', count: 18, severity: 'high' },
              { type: 'System Resources', count: 12, severity: 'critical' },
              { type: 'User Behavior', count: 9, severity: 'medium' },
              { type: 'API Requests', count: 8, severity: 'low' },
            ].map((anomaly) => (
              <div key={anomaly.type} className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-slate-900 dark:text-white">
                    {anomaly.type}
                  </div>
                  <div className="text-sm text-slate-500 dark:text-slate-400">
                    {anomaly.count} anomalies detected
                  </div>
                </div>
                <Badge variant={anomaly.severity as any}>
                  {anomaly.severity.charAt(0).toUpperCase() + anomaly.severity.slice(1)}
                </Badge>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Recent Anomalies" subtitle="Latest detected issues">
          <div className="space-y-4">
            {[
              {
                id: 1,
                title: 'Unusual Network Traffic Spike',
                timestamp: '2025-04-22T14:30:00Z',
                severity: 'critical',
                description: 'Detected 500% increase in outbound traffic',
              },
              {
                id: 2,
                title: 'Memory Usage Anomaly',
                timestamp: '2025-04-22T14:15:00Z',
                severity: 'high',
                description: 'Memory usage exceeded normal patterns',
              },
              {
                id: 3,
                title: 'Failed Login Attempts',
                timestamp: '2025-04-22T14:00:00Z',
                severity: 'medium',
                description: 'Multiple failed logins from same IP',
              },
            ].map((anomaly) => (
              <div 
                key={anomaly.id}
                className="border-b border-slate-200 dark:border-slate-700/50 last:border-0 pb-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-medium text-slate-900 dark:text-white">
                      {anomaly.title}
                    </div>
                    <div className="text-sm text-slate-500 dark:text-slate-400">
                      {new Date(anomaly.timestamp).toLocaleString()}
                    </div>
                    <div className="text-sm text-slate-600 dark:text-slate-300 mt-1">
                      {anomaly.description}
                    </div>
                  </div>
                  <Badge variant={anomaly.severity as any}>
                    {anomaly.severity.charAt(0).toUpperCase() + anomaly.severity.slice(1)}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="ML Model Performance" subtitle="Detection accuracy metrics">
          <div className="space-y-4">
            {[
              { metric: 'True Positives', value: 92.5, color: 'bg-green-500' },
              { metric: 'False Positives', value: 4.8, color: 'bg-amber-500' },
              { metric: 'False Negatives', value: 2.7, color: 'bg-red-500' },
            ].map((metric) => (
              <div key={metric.metric}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                    {metric.metric}
                  </span>
                  <span className="text-sm text-slate-500 dark:text-slate-400">
                    {metric.value}%
                  </span>
                </div>
                <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                  <div 
                    className={`${metric.color} h-2 rounded-full`}
                    style={{ width: `${metric.value}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};