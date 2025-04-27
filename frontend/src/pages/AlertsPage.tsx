import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Filter, Search, SlidersHorizontal } from 'lucide-react';
import { alerts } from '../data/mockData';
import { Alert } from '../types';


export const AlertsPage: React.FC = () => {
  const [selectedSeverity, setSelectedSeverity] = useState<string[]>([]);
  const [selectedStatus, setSelectedStatus] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAlerts = alerts.filter(alert => {
    const matchesSeverity = selectedSeverity.length === 0 || selectedSeverity.includes(alert.severity);
    const matchesStatus = selectedStatus.length === 0 || selectedStatus.includes(alert.status);
    const matchesSearch = searchQuery === '' || 
      alert.ip.toLowerCase().includes(searchQuery.toLowerCase()) ||
      alert.location.toLowerCase().includes(searchQuery.toLowerCase()) ||
      alert.type.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesSeverity && matchesStatus && matchesSearch;
  });

  const severityOptions = ['critical', 'high', 'medium', 'low'];
  const statusOptions = ['new', 'investigating', 'resolved', 'false-positive'];

  const toggleSeverity = (severity: string) => {
    setSelectedSeverity(prev => 
      prev.includes(severity) 
        ? prev.filter(s => s !== severity)
        : [...prev, severity]
    );
  };

  const toggleStatus = (status: string) => {
    setSelectedStatus(prev => 
      prev.includes(status) 
        ? prev.filter(s => s !== status)
        : [...prev, status]
    );
  };

  const AlertRow: React.FC<{ alert: Alert }> = ({ alert }) => {
    const formattedTime = new Date(alert.timestamp).toLocaleString();
    
    return (
      <tr className="border-b border-slate-200 dark:border-slate-700/50">
        <td className="py-4 px-4">
          <Badge variant={alert.severity as any}>{alert.severity}</Badge>
        </td>
        <td className="py-4 px-4">
          <div className="font-medium text-slate-900 dark:text-white">{alert.type}</div>
          <div className="text-sm text-slate-500 dark:text-slate-400">{alert.ip}</div>
        </td>
        <td className="py-4 px-4">
          <div>{alert.location}</div>
          <div className="text-sm text-slate-500 dark:text-slate-400">{formattedTime}</div>
        </td>
        <td className="py-4 px-4">
          <Badge variant="neutral">{alert.status}</Badge>
        </td>
        <td className="py-4 px-4">
          {alert.enrichment && (
            <div>
              <div className="text-sm">
                Abuse Score: {alert.enrichment.abuseScore}
              </div>
              <div className="text-sm text-slate-500 dark:text-slate-400">
                Previous Incidents: {alert.enrichment.previousIncidents}
              </div>
            </div>
          )}
        </td>
        <td className="py-4 px-4 text-right">
          <Button variant="ghost" size="sm">View Details</Button>
        </td>
      </tr>
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
            <input
              type="search"
              placeholder="Search alerts by IP, location, or type..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-4 ml-4">
          <Button variant="outline" icon={<Filter size={16} />}>
            Filter
          </Button>
          <Button variant="outline" icon={<SlidersHorizontal size={16} />}>
            Customize
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {severityOptions.map(severity => (
          <Button
            key={severity}
            variant={selectedSeverity.includes(severity) ? 'primary' : 'outline'}
            size="sm"
            onClick={() => toggleSeverity(severity)}
          >
            {severity}
          </Button>
        ))}
        <div className="mx-2 border-r border-slate-200 dark:border-slate-700" />
        {statusOptions.map(status => (
          <Button
            key={status}
            variant={selectedStatus.includes(status) ? 'primary' : 'outline'}
            size="sm"
            onClick={() => toggleStatus(status)}
          >
            {status}
          </Button>
        ))}
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700/50">
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500 dark:text-slate-400">Severity</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500 dark:text-slate-400">Alert</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500 dark:text-slate-400">Location</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500 dark:text-slate-400">Status</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500 dark:text-slate-400">Enrichment</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-slate-500 dark:text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAlerts.map(alert => (
                <AlertRow key={alert.id} alert={alert} />
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};