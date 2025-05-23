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

import React, { useState } from 'react';
import { 
  Activity,
  AlertTriangle,
  BarChart as BarChartIcon,
  Calendar,
  Download,
  FileText,
  Filter,
  Printer,
  RefreshCw,
  Shield,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import Input from '../../components/common/Input';
import Select from '../../components/common/Select';
import { mockAlertTrendData, mockReports } from '../../services/mockData';

const ReportingAnalyticsPage: React.FC = () => {
  const [dateRange, setDateRange] = useState('7d');
  const [reportType, setReportType] = useState('all');
  
  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Reporting & Analytics</h1>
          <p className="text-foreground/70">View security insights and generate reports</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<RefreshCw size={14} />}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<FileText size={14} />}
          >
            Generate Report
          </Button>
        </div>
      </div>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-foreground/70">Total Alerts</p>
                <p className="mt-1 text-2xl font-semibold">1,284</p>
              </div>
              <div className="rounded-full bg-primary/10 p-3">
                <AlertTriangle className="h-6 w-6 text-primary" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-xs">
              <span className="text-success">+12.4%</span>
              <span className="ml-2 text-foreground/70">vs last week</span>
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-foreground/70">Security Score</p>
                <p className="mt-1 text-2xl font-semibold">86%</p>
              </div>
              <div className="rounded-full bg-success/10 p-3">
                <Shield className="h-6 w-6 text-success" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-xs">
              <span className="text-success">+3.2%</span>
              <span className="ml-2 text-foreground/70">vs last month</span>
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-foreground/70">Active Threats</p>
                <p className="mt-1 text-2xl font-semibold">23</p>
              </div>
              <div className="rounded-full bg-error/10 p-3">
                <Activity className="h-6 w-6 text-error" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-xs">
              <span className="text-error">+8.1%</span>
              <span className="ml-2 text-foreground/70">vs last week</span>
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-foreground/70">Resolved Issues</p>
                <p className="mt-1 text-2xl font-semibold">892</p>
              </div>
              <div className="rounded-full bg-secondary/10 p-3">
                <BarChartIcon className="h-6 w-6 text-secondary" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-xs">
              <span className="text-success">+24.5%</span>
              <span className="ml-2 text-foreground/70">vs last month</span>
            </div>
          </div>
        </Card>
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <div className="p-6">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Alert Trends</h2>
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
                <LineChart data={mockAlertTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => new Date(value).getDate().toString()}
                  />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="critical" 
                    stroke="#EF4444" 
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="high" 
                    stroke="#F97316" 
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="medium" 
                    stroke="#F59E0B" 
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="p-6">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Attack Distribution</h2>
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
                <BarChart data={mockAlertTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => new Date(value).getDate().toString()}
                  />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="critical" fill="#EF4444" />
                  <Bar dataKey="high" fill="#F97316" />
                  <Bar dataKey="medium" fill="#F59E0B" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Card>
      </div>
      
      {/* Reports List */}
      <Card>
        <div className="p-6">
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="text-lg font-semibold">Generated Reports</h2>
            <div className="flex items-center gap-2">
              <Input
                placeholder="Search reports..."
                className="w-full sm:w-64"
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
                  { value: 'all', label: 'All Types' },
                  { value: 'monthly', label: 'Monthly' },
                  { value: 'threat', label: 'Threat' },
                  { value: 'activity', label: 'Activity' },
                  { value: 'compliance', label: 'Compliance' },
                ]}
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className="w-full sm:w-40"
              />
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Report Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">Generated</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-foreground/70 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {mockReports.map((report) => (
                  <tr key={report.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <FileText className="h-5 w-5 text-foreground/70" />
                        <span className="ml-2">{report.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                        {report.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground/70">
                      {new Date(report.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          leftIcon={<Download size={14} />}
                          aria-label="Download"
                        />
                        <Button
                          variant="ghost"
                          size="sm"
                          leftIcon={<Printer size={14} />}
                          aria-label="Print"
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ReportingAnalyticsPage;