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

import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  Clock,
  Shield,
  ShieldCheck,
  AlertOctagon,
  FileText,
  Server,
  Users,
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useEnhancedDashboardStore } from '../../features/dashboard/store/enhancedDashboardStore';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import TimeRangeSelector from '../../components/dashboard/TimeRangeSelector';
import RefreshControl from '../../components/dashboard/RefreshControl';
import DetailModal from '../../components/dashboard/DetailModal';
import AttackerDetails from '../../components/dashboard/AttackerDetails';
import AttackVectorDetails from '../../components/dashboard/AttackVectorDetails';

const EnhancedDashboardPage: React.FC = () => {
  const {
    securityMetrics,
    alertTrends,
    alertSeverityDistribution,
    topAttackVectors,
    topAttackers,
    complianceStatus,
    digitalTwinStatus,
    isLoading,
    lastUpdated,
    filters,
    refreshData,
    setFilters,
    startAutoRefresh,
    stopAutoRefresh,
  } = useEnhancedDashboardStore();

  // Drill-down state
  const [selectedAttacker, setSelectedAttacker] = useState<string | null>(null);
  const [selectedAttackVector, setSelectedAttackVector] = useState<string | null>(null);

  // Load data on mount
  useEffect(() => {
    refreshData();
    // Clean up auto-refresh on unmount
    return () => {
      stopAutoRefresh();
    };
  }, [refreshData, stopAutoRefresh]);

  const handleTimeRangeChange = (timeRange) => {
    setFilters({ timeRange });
  };

  const handleRefreshIntervalChange = (interval) => {
    setFilters({ refreshInterval: interval });
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Security Dashboard</h1>
          <p className="text-muted-foreground">Overview of your organization's security posture</p>
        </div>
        <div className="flex flex-col md:flex-row gap-4">
          <TimeRangeSelector
            currentRange={filters.timeRange}
            onChange={handleTimeRangeChange}
          />
          <RefreshControl
            lastUpdated={lastUpdated}
            isLoading={isLoading}
            refreshInterval={filters.refreshInterval}
            onRefresh={refreshData}
            onAutoRefreshChange={handleRefreshIntervalChange}
          />
        </div>
      </div>

      {/* Top cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {/* Security Posture */}
        <Card
          className="col-span-1"
          title="Security Posture"
          isLoading={isLoading}
        >
          <div className="flex flex-col items-center">
            <div className="relative w-32 h-32">
              <svg viewBox="0 0 100 50" className="w-full">
                {/* Background arc */}
                <path
                  d="M 0,50 A 50,50 0 0,1 100,50"
                  fill="none"
                  stroke="#1f2937"
                  strokeWidth="10"
                  strokeLinecap="round"
                />
                {/* Foreground arc (colored based on score) */}
                <path
                  d="M 0,50 A 50,50 0 0,1 100,50"
                  fill="none"
                  stroke={securityMetrics?.risk_score > 70 ? '#f59e0b' :
                          securityMetrics?.risk_score > 40 ? '#fbbf24' : '#10b981'}
                  strokeWidth="10"
                  strokeDasharray="157"
                  strokeDashoffset={157 - (157 * (securityMetrics?.risk_score || 0)) / 100}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold">{securityMetrics?.risk_score || 0}</span>
                <span className="text-xs text-amber-500">
                  {securityMetrics?.risk_score > 70 ? 'High Risk' :
                   securityMetrics?.risk_score > 40 ? 'Medium Risk' : 'Low Risk'}
                </span>
              </div>
            </div>
            <p className="mt-2 text-sm text-center text-muted-foreground">
              {securityMetrics?.risk_score > 70 ? 'Your security posture requires attention. Review critical alerts.' :
               securityMetrics?.risk_score > 40 ? 'Your security posture needs improvement.' : 'Your security posture is good.'}
            </p>
          </div>
        </Card>

        {/* Active Alerts */}
        <Card
          className="col-span-1"
          title="Active Alerts"
          isLoading={isLoading}
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertOctagon className="h-5 w-5 text-red-500" />
                <span>Critical</span>
              </div>
              <span className="font-bold text-red-500">{securityMetrics?.alerts_by_severity.critical || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                <span>High</span>
              </div>
              <span className="font-bold text-amber-500">{securityMetrics?.alerts_by_severity.high || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                <span>Medium</span>
              </div>
              <span className="font-bold text-yellow-500">{securityMetrics?.alerts_by_severity.medium || 0}</span>
            </div>
            <div className="mt-2">
              <Button
                variant="link"
                size="sm"
                className="p-0 h-auto"
                rightIcon={<ArrowRight size={14} />}
              >
                View all alerts
              </Button>
            </div>
          </div>
        </Card>

        {/* Digital Twin Status */}
        <Card
          className="col-span-1"
          title="Digital Twin Status"
          isLoading={isLoading}
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-blue-500" />
                <span>Active Twins</span>
              </div>
              <span className="font-bold">{digitalTwinStatus?.activeTwins || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Server className="h-5 w-5 text-blue-500" />
                <span>Honeypots</span>
              </div>
              <span className="font-bold">{digitalTwinStatus?.honeypots || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-blue-500" />
                <span>Engagements (24h)</span>
              </div>
              <span className="font-bold">{digitalTwinStatus?.engagements || 0}</span>
            </div>
            <div className="mt-2">
              <Button
                variant="link"
                size="sm"
                className="p-0 h-auto"
                rightIcon={<ArrowRight size={14} />}
              >
                View details
              </Button>
            </div>
          </div>
        </Card>

        {/* Compliance Status */}
        <Card
          className="col-span-1"
          title="Compliance Status"
          isLoading={isLoading}
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-gray-500" />
                <span>DPDP Act</span>
              </div>
              <span className={`font-bold ${complianceStatus?.dpdp.compliant ? 'text-green-500' : 'text-red-500'}`}>
                {complianceStatus?.dpdp.status || 'Unknown'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-gray-500" />
                <span>GDPR</span>
              </div>
              <span className={`font-bold ${complianceStatus?.gdpr.compliant ? 'text-green-500' : 'text-amber-500'}`}>
                {complianceStatus?.gdpr.status || 'Unknown'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-gray-500" />
                <span>ISO 27001</span>
              </div>
              <span className={`font-bold ${complianceStatus?.iso27001.compliant ? 'text-green-500' : 'text-red-500'}`}>
                {complianceStatus?.iso27001.status || 'Unknown'}
              </span>
            </div>
            <div className="mt-2">
              <Button
                variant="link"
                size="sm"
                className="p-0 h-auto"
                rightIcon={<ArrowRight size={14} />}
              >
                View reports
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Charts section */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Alert Trends */}
        <Card
          className="col-span-1 lg:col-span-2"
          title="Alert Trends"
          subtitle={`Last ${filters.timeRange === '24h' ? '24 hours' :
                          filters.timeRange === '7d' ? '7 days' :
                          filters.timeRange === '90d' ? '90 days' : '30 days'}`}
          isLoading={isLoading}
        >
          <div className="h-80">
            {alertTrends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={alertTrends}
                  margin={{ top: 20, right: 30, left: 0, bottom: 20 }}
                  stackOffset="sign"
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(value) => new Date(value).getDate().toString()}
                    fontSize={12}
                  />
                  <YAxis fontSize={12} />
                  <Tooltip
                    formatter={(value, name) => [value, name.charAt(0).toUpperCase() + name.slice(1)]}
                    labelFormatter={(label) => new Date(label).toLocaleDateString()}
                  />
                  <Bar dataKey="critical" stackId="a" fill="#EF4444" />
                  <Bar dataKey="high" stackId="a" fill="#F59E0B" />
                  <Bar dataKey="medium" stackId="a" fill="#FBBF24" />
                  <Bar dataKey="low" stackId="a" fill="#10B981" />
                  <Bar dataKey="info" stackId="a" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center">
                <p className="text-muted-foreground">No data available</p>
              </div>
            )}
          </div>
        </Card>

        {/* Alert Severity Distribution */}
        <Card
          className="col-span-1"
          title="Alert Severity Distribution"
          isLoading={isLoading}
        >
          <div className="h-80">
            {alertSeverityDistribution.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={alertSeverityDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                    labelLine={false}
                  >
                    {alertSeverityDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [`${value} alerts`, '']}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center">
                <p className="text-muted-foreground">No data available</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Bottom section */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Top Attack Vectors */}
        <Card
          title="Top Attack Vectors"
          isLoading={isLoading}
        >
          <div className="space-y-3 p-4">
            {topAttackVectors.length > 0 ? (
              topAttackVectors.map((vector, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted p-2 rounded-md transition-colors"
                  onClick={() => setSelectedAttackVector(vector.name)}
                >
                  <div className="flex items-center gap-2">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-medium text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                      {index + 1}
                    </span>
                    <span>{vector.name}</span>
                  </div>
                  <span className="font-medium">{vector.count} alerts</span>
                </div>
              ))
            ) : (
              <div className="flex h-40 items-center justify-center">
                <p className="text-muted-foreground">No data available</p>
              </div>
            )}
            <div className="mt-2">
              <Button
                variant="link"
                size="sm"
                className="p-0 h-auto"
                rightIcon={<ArrowRight size={14} />}
              >
                View all attack vectors
              </Button>
            </div>
          </div>
        </Card>

        {/* Top Attackers */}
        <Card
          title="Top Attackers"
          isLoading={isLoading}
        >
          <div className="space-y-3 p-4">
            {topAttackers.length > 0 ? (
              topAttackers.map((attacker, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between cursor-pointer hover:bg-muted p-2 rounded-md transition-colors"
                  onClick={() => setSelectedAttacker(attacker.ip)}
                >
                  <div className="flex items-center gap-2">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-red-100 text-xs font-medium text-red-800 dark:bg-red-900/30 dark:text-red-400">
                      {index + 1}
                    </span>
                    <span>{attacker.ip}</span>
                    <span className="text-xs text-muted-foreground">{attacker.country}</span>
                  </div>
                  <span className="font-medium">{attacker.count} attempts</span>
                </div>
              ))
            ) : (
              <div className="flex h-40 items-center justify-center">
                <p className="text-muted-foreground">No data available</p>
              </div>
            )}
            <div className="mt-2">
              <Button
                variant="link"
                size="sm"
                className="p-0 h-auto"
                rightIcon={<ArrowRight size={14} />}
              >
                View all attackers
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Drill-down modals */}
      <DetailModal
        title={`Attacker Details: ${selectedAttacker}`}
        isOpen={!!selectedAttacker}
        onClose={() => setSelectedAttacker(null)}
      >
        {selectedAttacker && <AttackerDetails ip={selectedAttacker} />}
      </DetailModal>

      <DetailModal
        title={`Attack Vector Details: ${selectedAttackVector}`}
        isOpen={!!selectedAttackVector}
        onClose={() => setSelectedAttackVector(null)}
      >
        {selectedAttackVector && <AttackVectorDetails vectorName={selectedAttackVector} />}
      </DetailModal>
    </div>
  );
};

export default EnhancedDashboardPage;