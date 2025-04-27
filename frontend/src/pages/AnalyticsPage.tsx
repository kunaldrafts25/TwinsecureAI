import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { LineChart, BarChart2, PieChart as PieChartIcon, TrendingUp } from 'lucide-react';
import { 
  LineChart as RechartsLineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { attackTrends, payloadTypes, systemMetrics } from '../data/mockData';

const COLORS = ['#6366f1', '#3b82f6', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b'];

export const AnalyticsPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [metricType, setMetricType] = useState('attacks');
  
  const totalAttacks = attackTrends.reduce((sum, day) => sum + day.blockedAttacks, 0);
  const avgDailyAttacks = Math.round(totalAttacks / attackTrends.length);

  // Format data for charts
  const formattedTrends = attackTrends.map(trend => ({
    ...trend,
    date: new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }));

  const errorRateData = systemMetrics.map(metric => ({
    time: new Date(metric.timestamp).toLocaleTimeString(),
    rate: metric.errorRate
  }));
  
  return (
    <div className="p-6 space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
              <TrendingUp size={24} className="text-indigo-600 dark:text-indigo-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Total Attacks</h3>
              <p className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
                {totalAttacks.toLocaleString()}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <BarChart2 size={24} className="text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Daily Average</h3>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {avgDailyAttacks.toLocaleString()}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <LineChart size={24} className="text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Success Rate</h3>
              <p className="text-3xl font-bold text-green-600 dark:text-green-400">99.9%</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
              <PieChartIcon size={24} className="text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Attack Types</h3>
              <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                {payloadTypes.length}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="space-x-2">
          {['24h', '7d', '30d', '90d'].map(range => (
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
          {['attacks', 'traffic', 'response', 'errors'].map(metric => (
            <Button
              key={metric}
              variant={metricType === metric ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setMetricType(metric)}
            >
              {metric.charAt(0).toUpperCase() + metric.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Main Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Attack Trends" subtitle="Historical attack patterns">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsLineChart data={formattedTrends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'rgb(15 23 42)',
                    border: 'none',
                    borderRadius: '0.5rem',
                    padding: '1rem',
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="blockedAttacks" 
                  stroke="#6366f1" 
                  name="Blocked Attacks"
                />
                <Line 
                  type="monotone" 
                  dataKey="honeypotHits" 
                  stroke="#8b5cf6" 
                  name="Honeypot Hits"
                />
              </RechartsLineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Attack Distribution" subtitle="Attack types breakdown">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={payloadTypes}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {payloadTypes.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'rgb(15 23 42)',
                    border: 'none',
                    borderRadius: '0.5rem',
                    padding: '1rem',
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Response Times" subtitle="System performance metrics">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={systemMetrics}>
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
                <Legend />
                <Bar dataKey="requests" fill="#6366f1" name="Requests/min" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Error Rates" subtitle="System reliability metrics">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsLineChart data={errorRateData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgb(15 23 42)',
                    border: 'none',
                    borderRadius: '0.5rem',
                    padding: '1rem',
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="rate" 
                  stroke="#ef4444" 
                  name="Error Rate"
                />
              </RechartsLineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
};