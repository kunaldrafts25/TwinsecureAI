import React from 'react';
import { AlertTriangle, ArrowRight, Shield, Zap, Database, Code } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Alert } from '../../types';
import { Button } from '../ui/Button';

type AlertItemProps = {
  alert: Alert;
  onViewDetails: (alertId: string) => void;
};

const getAlertIcon = (type: string) => {
  switch (type) {
    case 'Honeypot Triggered':
      return <Shield className="text-amber-500" size={18} />;
    case 'Anomaly Detected':
      return <Zap className="text-purple-500" size={18} />;
    case 'Brute Force':
      return <AlertTriangle className="text-orange-500" size={18} />;
    case 'SQL Injection':
      return <Database className="text-red-500" size={18} />;
    case 'XSS Attempt':
      return <Code className="text-blue-500" size={18} />;
    default:
      return <AlertTriangle className="text-slate-500" size={18} />;
  }
};

const getSeverityBadge = (severity: string) => {
  switch (severity) {
    case 'critical':
      return <Badge variant="critical">Critical</Badge>;
    case 'high':
      return <Badge variant="high">High</Badge>;
    case 'medium':
      return <Badge variant="medium">Medium</Badge>;
    case 'low':
      return <Badge variant="low">Low</Badge>;
    default:
      return <Badge variant="neutral">Unknown</Badge>;
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'new':
      return <Badge variant="critical">New</Badge>;
    case 'investigating':
      return <Badge variant="medium">Investigating</Badge>;
    case 'resolved':
      return <Badge variant="low">Resolved</Badge>;
    case 'false-positive':
      return <Badge variant="neutral">False Positive</Badge>;
    default:
      return <Badge variant="neutral">Unknown</Badge>;
  }
};

const AlertItem: React.FC<AlertItemProps> = ({ alert, onViewDetails }) => {
  const formattedTime = new Date(alert.timestamp).toLocaleTimeString();
  
  return (
    <div className="border-b border-slate-200 dark:border-slate-700/50 last:border-0 py-3">
      <div className="flex items-start space-x-3">
        <div className="pt-0.5">{getAlertIcon(alert.type)}</div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <h4 className="text-sm font-medium text-slate-900 dark:text-white">{alert.type}</h4>
            {getSeverityBadge(alert.severity)}
            {getStatusBadge(alert.status)}
          </div>
          
          <div className="flex items-center text-sm text-slate-500 dark:text-slate-400 mb-1 flex-wrap gap-2">
            <span>IP: {alert.ip}</span>
            <span>•</span>
            <span>{alert.location}</span>
            <span>•</span>
            <span>{formattedTime}</span>
          </div>
          
          {alert.payload && (
            <p className="mt-1 text-xs font-mono bg-slate-50 dark:bg-slate-800 p-1.5 rounded truncate">
              {alert.payload}
            </p>
          )}
        </div>
        
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => onViewDetails(alert.id)}
          icon={<ArrowRight size={14} />}
          iconPosition="right"
        >
          Details
        </Button>
      </div>
    </div>
  );
};

type AlertsListProps = {
  alerts: Alert[];
  onViewDetails: (alertId: string) => void;
};

export const AlertsList: React.FC<AlertsListProps> = ({ alerts, onViewDetails }) => {
  return (
    <Card title="Recent Alerts" subtitle="Latest security incidents">
      <div className="space-y-0 -mt-3">
        {alerts.map((alert) => (
          <AlertItem key={alert.id} alert={alert} onViewDetails={onViewDetails} />
        ))}
      </div>
      <div className="mt-3 text-center">
        <Button variant="ghost" size="sm" icon={<ArrowRight size={16} />} iconPosition="right">
          View all alerts
        </Button>
      </div>
    </Card>
  );
};