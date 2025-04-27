import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { FileText, Download, Filter, Calendar, ChevronDown } from 'lucide-react';
import { format } from 'date-fns';
import { reports } from '../data/mockData';

export const ReportsPage: React.FC = () => {
  const [reportType, setReportType] = useState('all');
  const [timeRange, setTimeRange] = useState('7d');
  
  return (
    <div className="p-6 space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <FileText size={24} className="text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Total Reports</h3>
              <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">{reports.length}</p>
            </div>
          </div>
        </Card>

        {[
          { title: 'Weekly Reports', count: 4, color: 'green' },
          { title: 'Monthly Reports', count: 1, color: 'purple' },
          { title: 'Custom Reports', count: 2, color: 'amber' },
        ].map((stat) => (
          <Card key={stat.title}>
            <div className="flex items-center">
              <div className={`p-3 bg-${stat.color}-100 dark:bg-${stat.color}-900/30 rounded-lg`}>
                <FileText size={24} className={`text-${stat.color}-600 dark:text-${stat.color}-400`} />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{stat.title}</h3>
                <p className={`text-3xl font-bold text-${stat.color}-600 dark:text-${stat.color}-400`}>
                  {stat.count}
                </p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="space-x-2">
          {['7d', '30d', '90d', 'all'].map(range => (
            <Button
              key={range}
              variant={timeRange === range ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setTimeRange(range)}
            >
              {range === 'all' ? 'All Time' : `Last ${range}`}
            </Button>
          ))}
        </div>
        
        <div className="border-l border-slate-200 dark:border-slate-700 h-6 mx-2" />
        
        <div className="space-x-2">
          {['all', 'weekly', 'monthly', 'incident', 'audit'].map(type => (
            <Button
              key={type}
              variant={reportType === type ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setReportType(type)}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {reports.map((report) => (
          <Card key={report.id}>
            <div className="flex items-start justify-between">
              <div className="flex items-start">
                <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded">
                  <FileText size={20} className="text-slate-600 dark:text-slate-400" />
                </div>
                <div className="ml-4">
                  <h3 className="text-lg font-medium text-slate-900 dark:text-white">
                    {report.title}
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                    {report.summary}
                  </p>
                  <div className="flex items-center mt-2 space-x-2">
                    <Badge variant="neutral">
                      {format(new Date(report.date), 'MMM d, yyyy')}
                    </Badge>
                    <Badge variant={report.status === 'published' ? 'low' : 'medium'}>
                      {report.status}
                    </Badge>
                  </div>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                icon={<Download size={16} />}
                iconPosition="right"
              >
                Download
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Generate Report Section */}
      <Card title="Generate Custom Report" subtitle="Create a new security report">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Report Type
              </label>
              <div className="relative">
                <select className="block w-full pl-3 pr-10 py-2 text-base border-slate-300 dark:border-slate-600 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md dark:bg-slate-800">
                  <option>Security Overview</option>
                  <option>Threat Analysis</option>
                  <option>Compliance Report</option>
                  <option>Incident Summary</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                  <ChevronDown size={16} className="text-slate-400" />
                </div>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Time Period
              </label>
              <div className="relative">
                <select className="block w-full pl-3 pr-10 py-2 text-base border-slate-300 dark:border-slate-600 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md dark:bg-slate-800">
                  <option>Last 7 days</option>
                  <option>Last 30 days</option>
                  <option>Last 90 days</option>
                  <option>Custom range</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                  <ChevronDown size={16} className="text-slate-400" />
                </div>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Include Sections
            </label>
            <div className="space-y-2">
              {[
                'Executive Summary',
                'Threat Analysis',
                'Security Metrics',
                'Incident Details',
                'Recommendations',
              ].map((section) => (
                <label key={section} className="flex items-center">
                  <input
                    type="checkbox"
                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-800"
                    defaultChecked
                  />
                  <span className="ml-2 text-sm text-slate-600 dark:text-slate-400">
                    {section}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <Button variant="outline">Cancel</Button>
            <Button>Generate Report</Button>
          </div>
        </div>
      </Card>
    </div>
  );
};