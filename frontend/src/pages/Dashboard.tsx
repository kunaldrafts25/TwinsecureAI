import React from 'react';
import { ShieldAlert, Eye, ServerCrash, Users, Map } from 'lucide-react';
import { AlertsList } from '../components/dashboard/AlertsList';
import { StatCard } from '../components/dashboard/StatCard';
import { ThreatMap } from '../components/dashboard/ThreatMap';
import { AttackTrends } from '../components/dashboard/AttackTrends';
import { PayloadBreakdown } from '../components/dashboard/PayloadBreakdown';
import { SystemStatus } from '../components/dashboard/SystemStatus';
import { ReportsList } from '../components/dashboard/ReportsList';

import { alerts, attackOrigins, attackTrends, payloadTypes, systemMetrics, reports } from '../data/mockData';

export const Dashboard: React.FC = () => {
  const handleViewAlertDetails = (alertId: string) => {
    console.log(`View alert details for ${alertId}`);
    // In a real app, this would navigate to a detail view or open a modal
  };
  
  return (
    <div className="p-6 space-y-6">
      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Threats Blocked"
          value={24783}
          icon={<ShieldAlert size={20} className="text-red-600 dark:text-red-500" />}
          change={12}
          changeText="Increase from last week"
        />
        
        <StatCard
          title="Honeypot Triggers"
          value={1254}
          icon={<Eye size={20} className="text-amber-600 dark:text-amber-500" />}
          change={-8}
          changeText="Decrease from last week"
        />
        
        <StatCard
          title="System Anomalies"
          value={76}
          icon={<ServerCrash size={20} className="text-purple-600 dark:text-purple-500" />}
          change={5}
          changeText="Increase from last week"
        />
        
        <StatCard
          title="Protected Endpoints"
          value={128}
          icon={<Users size={20} className="text-green-600 dark:text-green-500" />}
        />
      </div>
      
      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column - wider */}
        <div className="lg:col-span-2 space-y-6">
          <AttackTrends trends={attackTrends} />
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ThreatMap attackOrigins={attackOrigins} />
            <PayloadBreakdown payloadTypes={payloadTypes} />
          </div>
          
          <SystemStatus metrics={systemMetrics} />
        </div>
        
        {/* Right column - narrower */}
        <div className="space-y-6">
          <AlertsList 
            alerts={alerts} 
            onViewDetails={handleViewAlertDetails} 
          />
          
          <ReportsList reports={reports} />
        </div>
      </div>
    </div>
  );
};