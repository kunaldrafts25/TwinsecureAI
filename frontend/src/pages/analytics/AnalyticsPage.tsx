import React, { useState } from 'react';
import { 
  BarChart as BarChartIcon,
  Calendar,
  Download,
  Filter,
  Printer,
  RefreshCw,
  Search,
  Shield,
  Sliders,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import Input from '../../components/common/Input';
import Select from '../../components/common/Select';
import { mockTTPFrequencyData } from '../../services/mockData';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

const AnalyticsPage: React.FC = () => {
  const [dateRange, setDateRange] = useState('7d');
  const [metricType, setMetricType] = useState('all');
  
  const attackPatterns = [
    { name: 'SQL Injection', value: 35 },
    { name: 'XSS', value: 28 },
    { name: 'Brute Force', value: 22 },
    { name: 'File Upload', value: 15 },
    { name: 'Command Injection', value: 10 },
  ];
  
  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Security Analytics</h1>
          <p className="text-foreground/70">Advanced security metrics and analysis</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<Calendar size={14} />}
          >
            Date Range
          </Button>
          <Button
            variant="outline"
            size="sm"
            leftIcon={<Download size={14} />}
          >
            Export
          </Button>
        </div>
      </div>
      
      {/* Metrics Overview */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <div className="p-6">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Attack Pattern Distribution</h2>
              <Select
                options={[
                  { value: '7d', label: 'Last 7 days' },
                  { value: '30d', label: 'Last 30 days' },
                  { value: '90d', label: 'Last 90 days' },
                ]}
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
              />
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={attackPatterns}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {attackPatterns.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="p-6">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-lg font-semibold">MITRE ATT&CK Coverage</h2>
              <Button
                variant="outline"
                size="sm"
                leftIcon={<Sliders size={14} />}
              >
                Configure
              </Button>
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mockTTPFrequencyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="id" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Card>
      </div>
      
      {/* Detailed Analysis */}
      <Card>
        <div className="p-6">
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-lg font-semibold">Security Metrics Analysis</h2>
            <div className="flex items-center gap-2">
              <Input
                placeholder="Search metrics..."
                className="w-full sm:w-64"
                leftIcon={<Search size={16} />}
              />
              <Button
                variant="outline"
                size="sm"
                leftIcon={<Filter size={14} />}
              >
                Filter
              </Button>
              <Select
                options={[
                  { value: 'all', label: 'All Metrics' },
                  { value: 'attacks', label: 'Attack Patterns' },
                  { value: 'vulnerabilities', label: 'Vulnerabilities' },
                  { value: 'compliance', label: 'Compliance' },
                ]}
                value={metricType}
                onChange={(e) => setMetricType(e.target.value)}
                className="w-full sm:w-40"
              />
            </div>
          </div>
          
          <div className="space-y-4">
            {[
              { name: 'Average Time to Detection', value: '2.3 hours', change: -15 },
              { name: 'False Positive Rate', value: '4.2%', change: -8 },
              { name: 'Security Coverage', value: '94%', change: 5 },
              { name: 'Risk Score Trend', value: '72/100', change: 3 },
              { name: 'Incident Response Time', value: '45 mins', change: -12 },
            ].map((metric, index) => (
              <div
                key={index}
                className="flex items-center justify-between rounded-lg border border-border bg-card/50 p-4"
              >
                <div>
                  <h3 className="font-medium">{metric.name}</h3>
                  <p className="text-2xl font-semibold text-primary">{metric.value}</p>
                </div>
                <div className={`text-sm ${metric.change > 0 ? 'text-success' : 'text-error'}`}>
                  {metric.change > 0 ? '+' : ''}{metric.change}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
      
      {/* Recommendations */}
      <Card>
        <div className="p-6">
          <h2 className="mb-4 text-lg font-semibold">Security Recommendations</h2>
          <div className="space-y-4">
            {[
              {
                title: 'Update Web Application Firewall Rules',
                priority: 'High',
                impact: 'Reduce XSS attacks by 45%',
              },
              {
                title: 'Enable Multi-Factor Authentication',
                priority: 'Critical',
                impact: 'Prevent 99% of automated attacks',
              },
              {
                title: 'Review Access Control Policies',
                priority: 'Medium',
                impact: 'Improve compliance score by 15%',
              },
            ].map((recommendation, index) => (
              <div
                key={index}
                className="flex items-center justify-between rounded-lg border border-border bg-card/50 p-4"
              >
                <div className="flex items-center gap-4">
                  <Shield className="h-8 w-8 text-primary" />
                  <div>
                    <h3 className="font-medium">{recommendation.title}</h3>
                    <p className="text-sm text-foreground/70">{recommendation.impact}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`rounded-full px-2 py-1 text-xs font-medium ${
                    recommendation.priority === 'Critical' ? 'bg-error/10 text-error' :
                    recommendation.priority === 'High' ? 'bg-warning/10 text-warning' :
                    'bg-success/10 text-success'
                  }`}>
                    {recommendation.priority}
                  </span>
                  <Button variant="outline" size="sm">
                    Review
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default AnalyticsPage;